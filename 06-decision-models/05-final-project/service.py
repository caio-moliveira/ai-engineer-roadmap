"""Regras da aplicação: roda o grafo, retoma depois da aprovação e acumula o resumo de economia.

As rotas (router.py) só traduzem HTTP para estas funções; o `demo.py` chama as mesmas funções
direto, sem subir a API.
"""

import logging
import uuid

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import Command

from config import get_settings
from graph import build_graph
from schemas import PerguntaIn, ResumoOut, RespostaOut, Totais

logger = logging.getLogger(__name__)

# Um checkpointer em memória para as três versões: guarda o estado das threads pausadas.
# Num serviço de verdade, troque por um checkpointer persistente (postgres ou redis).
_checkpointer = InMemorySaver()
_grafos = {versao: build_graph(versao, _checkpointer) for versao in ("v1", "v2", "v3")}
_versao_da_thread: dict[str, str] = {}

# Cada passo do agente com guardião são três nós (agente, guardiao, executar): o limite padrão
# de 25 do LangGraph é pouco para MAX_PASSOS = 8.
_RECURSION_LIMIT = 100

_contabilizadas: set[str] = set()
_resumo = {
    "perguntas": 0,
    "resolvidas_pelo_pequeno": 0,
    "cascatas": 0,
    "bloqueios": 0,
    "aprovacoes_humanas": 0,
    "jev_chamadas": 0,
    "jev_latencia_total_ms": 0.0,
    "llm_chamadas_pequeno": 0,
    "llm_chamadas_grande": 0,
    "custo_real_usd": 0.0,
    "custo_se_tudo_no_grande_usd": 0.0,
}


async def perguntar(entrada: PerguntaIn) -> RespostaOut:
    """Uma pergunta nova abre uma thread nova e roda o grafo até o fim ou até uma pausa."""
    versao = entrada.versao or get_settings().agent_version
    thread_id = uuid.uuid4().hex
    _versao_da_thread[thread_id] = versao

    pergunta = entrada.pergunta.strip()
    if entrada.contexto:
        pergunta = f"{entrada.contexto.strip()}\n\nEsclarecimento do usuário: {pergunta}"

    logger.info("[Agente] %s · thread %s · %s", versao, thread_id[:8], pergunta[:80])
    await _grafos[versao].ainvoke(
        {"pergunta": pergunta, "versao": versao, "modelo_inicial": entrada.modelo_inicial},
        _config(thread_id),
    )
    return await _montar_resposta(thread_id)


async def aprovar(thread_id: str, aprovado: bool) -> RespostaOut:
    """Retoma uma thread pausada pelo nó de aprovação, com a decisão da pessoa."""
    versao = _versao_da_thread.get(thread_id)
    if versao is None:
        raise KeyError(thread_id)
    snapshot = await _grafos[versao].aget_state(_config(thread_id))
    if not snapshot.interrupts:
        raise ValueError("Esta conversa não está esperando aprovação.")

    logger.info("[Aprovação] thread %s · %s", thread_id[:8], "aprovada" if aprovado else "recusada")
    await _grafos[versao].ainvoke(Command(resume={"aprovado": aprovado}), _config(thread_id))
    return await _montar_resposta(thread_id)


def resumo() -> ResumoOut:
    r = _resumo
    economia = r["custo_se_tudo_no_grande_usd"] - r["custo_real_usd"]
    base = r["custo_se_tudo_no_grande_usd"]
    return ResumoOut(
        perguntas=r["perguntas"],
        resolvidas_pelo_pequeno=r["resolvidas_pelo_pequeno"],
        cascatas=r["cascatas"],
        bloqueios=r["bloqueios"],
        aprovacoes_humanas=r["aprovacoes_humanas"],
        jev_chamadas=r["jev_chamadas"],
        jev_latencia_media_ms=round(r["jev_latencia_total_ms"] / r["jev_chamadas"], 1) if r["jev_chamadas"] else 0,
        llm_chamadas_pequeno=r["llm_chamadas_pequeno"],
        llm_chamadas_grande=r["llm_chamadas_grande"],
        custo_real_usd=round(r["custo_real_usd"], 6),
        custo_se_tudo_no_grande_usd=round(base, 6),
        economia_usd=round(economia, 6),
        economia_pct=round(100 * economia / base, 1) if base else 0,
    )


# --- Internos ------------------------------------------------------------------------------------
def _config(thread_id: str) -> dict:
    return {"configurable": {"thread_id": thread_id}, "recursion_limit": _RECURSION_LIMIT}


def custo_usd(chamada: dict, tamanho: str | None = None) -> float:
    """Custo de uma chamada ao LLM com os preços do tamanho dado (ou do tamanho que ela usou)."""
    s = get_settings()
    tamanho = tamanho or chamada["tamanho"]
    preco_in, preco_out = (
        (s.price_large_in, s.price_large_out) if tamanho == "grande" else (s.price_small_in, s.price_small_out)
    )
    return (chamada["tokens_in"] * preco_in + chamada["tokens_out"] * preco_out) / 1_000_000


async def _montar_resposta(thread_id: str) -> RespostaOut:
    versao = _versao_da_thread[thread_id]
    snapshot = await _grafos[versao].aget_state(_config(thread_id))
    v = snapshot.values

    if snapshot.interrupts:
        status, pendente = "aguardando_aprovacao", snapshot.interrupts[0].value
    else:
        status, pendente = ("esclarecimento" if v.get("status") == "esclarecimento" else "concluida"), None

    trilha = v.get("trilha", [])
    chamadas = v.get("chamadas_llm", [])
    jev = [t for t in trilha if t["tipo"] == "jev"]
    totais = Totais(
        jev_chamadas=len(jev),
        jev_tokens_in=sum(t["tokens_in"] for t in jev),
        jev_tokens_out=sum(t["tokens_out"] for t in jev),
        jev_latencia_ms=round(sum(t["latencia_ms"] for t in jev), 1),
        llm_chamadas=len(chamadas),
        llm_tokens_in=sum(c["tokens_in"] for c in chamadas),
        llm_tokens_out=sum(c["tokens_out"] for c in chamadas),
        llm_latencia_ms=round(sum(c["latencia_ms"] for c in chamadas), 1),
        llm_custo_usd=round(sum(custo_usd(c) for c in chamadas), 6),
    )

    if status != "aguardando_aprovacao" and thread_id not in _contabilizadas:
        _contabilizadas.add(thread_id)
        _contabilizar(v, status)

    return RespostaOut(
        thread_id=thread_id,
        versao=versao,
        status=status,
        resposta=v.get("resposta", ""),
        aviso=v.get("aviso", ""),
        intencao=v.get("intencao", ""),
        modelo=v.get("modelo", "").split(":", 1)[-1],
        tentativas=v.get("tentativa", 0),
        aprovacao_pendente=pendente,
        passos=v.get("passos", []),
        trilha=trilha,
        chamadas_llm=chamadas,
        totais=totais,
    )


def _contabilizar(v: dict, status: str) -> None:
    r = _resumo
    trilha, chamadas = v.get("trilha", []), v.get("chamadas_llm", [])

    r["perguntas"] += 1
    if status == "concluida" and not v.get("aviso") and all(c["tamanho"] == "pequeno" for c in chamadas):
        r["resolvidas_pelo_pequeno"] += 1
    r["cascatas"] += max(v.get("tentativa", 1) - 1, 0)
    r["bloqueios"] += sum(p["status"] == "bloqueada" for p in v.get("passos", []))
    r["aprovacoes_humanas"] += sum(t["no"] == "aprovacao" for t in trilha)

    for t in trilha:
        if t["tipo"] == "jev":
            r["jev_chamadas"] += 1
            r["jev_latencia_total_ms"] += t["latencia_ms"]
    for c in chamadas:
        r[f"llm_chamadas_{c['tamanho']}"] += 1
        r["custo_real_usd"] += custo_usd(c)
        r["custo_se_tudo_no_grande_usd"] += custo_usd(c, "grande")
