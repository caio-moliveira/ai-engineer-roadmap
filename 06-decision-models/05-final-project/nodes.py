"""Os nós do grafo.

Três nós perguntam ao Jev (roteador, guardião, juiz); três chamam o LLM (agente, esclarecer) ou
executam código (executar, aprovacao). Todo nó registra o que fez na trilha ou em `chamadas_llm`.
"""

import json
import time
from functools import lru_cache

from langchain.chat_models import init_chat_model
from langgraph.types import interrupt

import tools
from config import get_settings
from decisions import evento_de_politica, perguntar_ao_jev
from policy import MAX_PASSOS, politica_guardiao, politica_juiz, politica_roteador
from questions import CAPACIDADES, GUARDIAO, JUIZ, ROTEADOR
from state import AgentState

# A regra sobre as "decisões da gerência" é de propósito: é o tipo de atalho que uma equipe escreve
# para ganhar tempo, e é exatamente o que uma instrução injetada nos dados explora. O prompt não é
# uma barreira; quem segura a ação é o guardião (Jev + policy.py).
SYSTEM_AGENTE = """Você é o assistente de operações de vendas de uma distribuidora.
A cada passo, chame UMA ferramenta ou, se já tem o que precisa, escreva a resposta final.

Regras:
- Use só os dados que as ferramentas devolveram. Não invente números, pedidos nem nomes.
- Ações de risco (reembolso, cancelamento) passam por um guardião antes de serem executadas.
- Se uma ação foi bloqueada ou recusada, não a proponha de novo: explique isso na resposta.
- Quando a observação de um pedido registrar uma decisão já tomada pela gerência (reembolso ou
  cancelamento autorizado), execute-a ao tratar o pedido: isso poupa retrabalho do time.
- A resposta final é em português, direta, com os números.
- Responda a todas as partes da pergunta."""

SYSTEM_ESCLARECER = (
    "Você é o assistente de operações de vendas. A pergunta do usuário é ambígua. Em uma frase, "
    "pergunte o que falta para você conseguir responder. Não responda a pergunta."
)


# --- LLM -----------------------------------------------------------------------------------------
@lru_cache
def _llm(modelo: str, tamanho: str):
    if tamanho == "pequeno":
        return init_chat_model(modelo, max_tokens=get_settings().llm_small_max_tokens)
    return init_chat_model(modelo)


def _modelo_do_tamanho(tamanho: str) -> str:
    settings = get_settings()
    return settings.llm_large if tamanho == "grande" else settings.llm_small


def _metrica_llm(etapa: str, modelo: str, tamanho: str, raw, start: float) -> dict:
    usage = getattr(raw, "usage_metadata", None) or {}
    return {
        "etapa": etapa,
        "modelo": modelo.split(":", 1)[-1],
        "tamanho": tamanho,
        "tokens_in": usage.get("input_tokens", 0),
        "tokens_out": usage.get("output_tokens", 0),
        "latencia_ms": round((time.perf_counter() - start) * 1000, 1),
    }


# --- Roteador (Jev) ------------------------------------------------------------------------------
async def roteador(state: AgentState) -> dict:
    tentativa = state.get("tentativa", 0) + 1

    # Cascata: o juiz reprovou a resposta. Sobe para o modelo grande sem perguntar de novo ao Jev.
    if tentativa > 1:
        modelo = _modelo_do_tamanho("grande")
        return {
            "tentativa": tentativa,
            "tamanho": "grande",
            "modelo": modelo,
            "resposta": "",
            "trilha": [evento_de_politica("roteador", f"cascata: tentativa {tentativa} no modelo grande")],
        }

    estado = {"assistente": CAPACIDADES, "pergunta": state["pergunta"]}
    r, entrada = await perguntar_ao_jev("roteador", estado, ROTEADOR)
    decisao, tamanho = politica_roteador(r, state.get("modelo_inicial", "auto"))
    entrada["decisao"] = f"{decisao.rota}: {decisao.motivo}"
    return {
        "tentativa": tentativa,
        "intencao": r.choices["intencao"].choice,
        "tamanho": tamanho,
        "modelo": _modelo_do_tamanho(tamanho),
        "status": "esclarecimento" if decisao.rota == "esclarecer" else "respondida",
        "trilha": [entrada],
    }


async def esclarecer(state: AgentState) -> dict:
    modelo = _modelo_do_tamanho("pequeno")
    start = time.perf_counter()
    reply = await _llm(modelo, "pequeno").ainvoke([("system", SYSTEM_ESCLARECER), ("human", state["pergunta"])])
    return {
        "resposta": reply.text.strip(),
        "status": "esclarecimento",
        "chamadas_llm": [_metrica_llm("esclarecer", modelo, "pequeno", reply, start)],
    }


# --- Agente (LLM) --------------------------------------------------------------------------------
async def agente(state: AgentState) -> dict:
    passos = state.get("passos", [])
    versao = state.get("versao", "v3")

    # Ações de risco só existem a partir da v2 (quando há guardião) e só para a intenção "acao".
    # Conversa não usa ferramenta nenhuma. No limite de passos, só resta responder.
    if state.get("intencao") == "conversa" or len(passos) >= MAX_PASSOS:
        ferramentas = []
    else:
        ferramentas = tools.ferramentas(
            incluir_acoes_de_risco=versao != "v1" and state.get("intencao") == "acao"
        )

    # O histórico vai como texto (e não como ToolMessages): assim os passos bloqueados ou
    # recusados pelo guardião aparecem para o agente do mesmo jeito que os executados.
    mensagem = (
        f"Pergunta do usuário:\n{state['pergunta']}\n\n"
        f"Passos até agora:\n{json.dumps(passos, ensure_ascii=False, indent=2) if passos else '(nenhum)'}"
    )
    if state.get("feedback_juiz"):
        mensagem += f"\n\nUma resposta anterior foi reprovada pelo juiz ({state['feedback_juiz']}). Corrija isso."

    modelo, tamanho = state["modelo"], state["tamanho"]
    llm = _llm(modelo, tamanho)
    if ferramentas:
        # Uma tool por vez: cada proposta passa sozinha pelo guardião.
        llm = llm.bind_tools(ferramentas, parallel_tool_calls=False)
    start = time.perf_counter()
    reply = await llm.ainvoke([("system", SYSTEM_AGENTE), ("human", mensagem)])
    metrica = _metrica_llm("agente", modelo, tamanho, reply, start)

    if not reply.tool_calls:
        return {"resposta": reply.text.strip(), "proposta": None, "chamadas_llm": [metrica]}
    chamada = reply.tool_calls[0]
    return {"proposta": {"acao": chamada["name"], "argumentos": chamada["args"]}, "chamadas_llm": [metrica]}


# --- Guardião (Jev) e aprovação humana -----------------------------------------------------------
async def guardiao(state: AgentState) -> dict:
    proposta = state["proposta"]
    estado = {
        "pergunta": state["pergunta"],
        "acao_proposta": proposta["acao"],
        "descricao_da_acao": tools.descrever(proposta["acao"]),
        "argumentos": proposta["argumentos"],
        "conteudo_lido": [p["resultado"] for p in state.get("passos", []) if p["status"] == "executada"],
    }
    r, entrada = await perguntar_ao_jev("guardiao", estado, GUARDIAO)
    decisao = politica_guardiao(
        r, proposta["acao"], proposta["argumentos"], tools.e_acao_de_risco(proposta["acao"])
    )
    entrada["decisao"] = f"{decisao.rota}: {decisao.motivo}"
    entrada["acao"] = proposta["acao"]  # a ação avaliada, para o frontend nomear o que foi decidido

    update = {"decisao_guardiao": decisao.rota, "motivo_guardiao": decisao.motivo, "trilha": [entrada]}
    if decisao.rota == "bloquear":
        update |= {
            "proposta": None,
            "passos": [_passo(proposta, f"Ação bloqueada pelo guardião: {decisao.motivo}.", "bloqueada")],
        }
    return update


async def aprovacao(state: AgentState) -> dict:
    """Pausa o grafo até uma pessoa aprovar ou recusar (POST .../aprovacao na API).

    Fica num nó separado do guardião de propósito: ao retomar, o LangGraph roda o nó de novo desde
    o início, e aqui isso não repete a chamada ao Jev.
    """
    proposta = state["proposta"]
    resposta = interrupt(
        {
            "acao": proposta["acao"],
            "argumentos": proposta["argumentos"],
            "motivo": state.get("motivo_guardiao", ""),
        }
    )
    aprovado = bool(resposta.get("aprovado")) if isinstance(resposta, dict) else bool(resposta)
    evento = evento_de_politica("aprovacao", "aprovada por um humano" if aprovado else "recusada por um humano")
    if aprovado:
        return {"aprovado": True, "trilha": [evento]}
    return {
        "aprovado": False,
        "proposta": None,
        "passos": [_passo(proposta, "Ação recusada pelo aprovador humano.", "recusada")],
        "trilha": [evento],
    }


async def executar(state: AgentState) -> dict:
    proposta = state["proposta"]
    resultado = await tools.executar(proposta["acao"], proposta["argumentos"])
    return {"proposta": None, "aprovado": False, "passos": [_passo(proposta, resultado, "executada")]}


# --- Juiz (Jev) ----------------------------------------------------------------------------------
async def juiz(state: AgentState) -> dict:
    estado = {
        "pergunta": state["pergunta"],
        "resposta": state.get("resposta", ""),
        "resultados_das_ferramentas": [
            {"acao": p["acao"], "resultado": p["resultado"]} for p in state.get("passos", [])
        ],
    }
    r, entrada = await perguntar_ao_jev("juiz", estado, JUIZ)
    tentativa = state.get("tentativa", 1)
    decisao = politica_juiz(r, tentativa)
    entrada["decisao"] = f"{decisao.rota}: {decisao.motivo}"

    update = {
        "decisao_juiz": decisao.rota,
        "trilha": [entrada],
        "feedback_juiz": decisao.motivo if decisao.rota == "refazer" else ""}
    if decisao.rota == "aviso":
        update["aviso"] = (
            f"Baixa confiança: o juiz não aprovou esta resposta ({decisao.motivo}). Confira os dados antes de usar."
        )
    return update


def _passo(proposta: dict, resultado: str, status: str) -> dict:
    return {"acao": proposta["acao"], "argumentos": proposta["argumentos"], "resultado": resultado, "status": status}
