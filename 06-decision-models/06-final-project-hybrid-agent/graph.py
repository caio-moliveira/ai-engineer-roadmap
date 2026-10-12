"""O grafo do agente híbrido de vendas.

    guardrail ─┬─ bloqueado ─────────────────────────────────────────────► fim
               └─ triagem ─┬─ nenhuma tool / baixa confiança ────────────► fim (sem dado / humano)
                           └─ consulta → gerar (LLM) → verificar ─┬─ aprovada ─► fim
                                                                  └─ reprovada ─► fim (resposta segura)

Quatro chamadas de modelo por pergunta respondida: três decisões (guardrail, triagem,
verificação) e UMA geração. Cada decisão vai para o provider configurado no node.
"""

from __future__ import annotations

import operator
import os
import sys
import time
from pathlib import Path
from typing import Annotated, Any

from typing_extensions import TypedDict

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # para importar `common`

import yaml
from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import END, START, StateGraph

from common.decisions import DecisionResult, DecisionSpec
from common.pricing import cost_usd
from common.providers import get_client
from common.providers.llm import model_kwargs
from common.providers.replay import ReplayMissError, cached_call
from common.specs import GUARDRAIL, NO_TOOL, TOOL, VERIFICACAO
from tools import run_tool

CONFIG_PATH = Path(__file__).with_name("config.yaml")

SYSTEM_GERACAO = (
    "Você é o assistente de dados de vendas da empresa Mercado Jornada. Responda em português, em até "
    "três frases, usando SÓ os dados recebidos. Cite os números como estão nos dados. Não faça previsões, "
    "não exponha dado pessoal e não recomende punição de pessoas."
)
MSG_BLOQUEADA = "Não posso ajudar com esse pedido. Posso responder perguntas sobre as vendas da empresa."
MSG_SEM_DADO = "Não tenho esse dado nas consultas disponíveis (vendas de jan/2025 a set/2026)."
MSG_HUMANO = "Encaminhei sua pergunta para um analista: não tenho certeza de qual consulta a responde."
MSG_REPROVADA = "Não consegui montar uma resposta confiável a partir dos dados. Encaminhei para um analista."


def load_config(path: Path = CONFIG_PATH) -> dict:
    config = yaml.safe_load(path.read_text(encoding="utf-8"))
    if override := os.environ.get("AGENTE_PROVIDER"):
        config["providers"] = {node: override for node in config["providers"]}
    return config


class AgentState(TypedDict, total=False):
    pergunta: str
    desfecho: str  # bloqueada | sem_dado | humano | aprovada | reprovada | sem_gravacao
    resposta: str
    tool: str | None
    dados: list[dict]
    rascunho: str
    sinais: dict[str, float]
    chamadas: Annotated[list[dict], operator.add]  # uma entrada por chamada de modelo


def _registro(node: str, result: DecisionResult) -> dict:
    return {"node": node, "tipo": "decisão", "provider": result.provider, "synthetic": result.synthetic,
            "latency_ms": result.latency_ms, "cost_usd": result.cost_usd or 0.0,
            "respostas": {k: v.value for k, v in result.answers.items()},
            "confiancas": {k: v.confidence for k, v in result.answers.items()}}


def build_graph(config: dict | None = None):
    config = config or load_config()
    providers, limiares = config["providers"], config["limiares"]
    clients = {node: get_client(target) for node, target in providers.items()}

    def decidir(node: str, state: Any, questions: list[DecisionSpec]) -> DecisionResult:
        return clients[node].decide(state, questions)

    def guardrail(state: AgentState) -> dict:
        result = decidir("guardrail", {"pergunta": state["pergunta"]}, GUARDRAIL)
        sinais = {k: float(v.value) for k, v in result.answers.items()}
        update = {"sinais": sinais, "chamadas": [_registro("guardrail", result)]}
        if any(p >= limiares["bloquear_guardrail"] for p in sinais.values()):
            update |= {"desfecho": "bloqueada", "resposta": MSG_BLOQUEADA}
        return update

    def triagem(state: AgentState) -> dict:
        result = decidir("triagem", {"pergunta": state["pergunta"]}, [TOOL])
        answer = result.answers.get("tool")
        update = {"tool": answer.value if answer else None, "chamadas": [_registro("triagem", result)]}
        if answer is None or answer.value not in TOOL.criteria:
            return update | {"desfecho": "humano", "resposta": MSG_HUMANO}
        if answer.value == NO_TOOL:
            return update | {"desfecho": "sem_dado", "resposta": MSG_SEM_DADO}
        if (answer.confidence or 0) < limiares["confianca_minima_triagem"]:
            return update | {"desfecho": "humano", "resposta": MSG_HUMANO}
        return update

    def consulta(state: AgentState) -> dict:
        return {"dados": run_tool(state["tool"])}  # nome vem do Choice: sempre uma tool do registro

    def gerar(state: AgentState) -> dict:
        model = config["geracao"]
        model_id = model.split(":", 1)[-1]
        request = {"tipo": "geracao", "modelo": model, "system": SYSTEM_GERACAO,
                   "pergunta": state["pergunta"], "dados": state["dados"]}

        def call() -> dict:
            llm = init_chat_model(model, **model_kwargs(model))
            start = time.perf_counter()
            msg = llm.invoke([SystemMessage(SYSTEM_GERACAO),
                              HumanMessage(f"Pergunta: {state['pergunta']}\n\nDados:\n{state['dados']}")])
            usage = msg.usage_metadata or {}
            return {"texto": msg.text if hasattr(msg, "text") else str(msg.content),
                    "latency_ms": (time.perf_counter() - start) * 1000,
                    "tokens_in": usage.get("input_tokens", 0), "tokens_out": usage.get("output_tokens", 0)}

        try:
            out = cached_call(f"geracao:{model}", request, call, origin=f"init_chat_model ({model})")
        except ReplayMissError:
            return {"desfecho": "sem_gravacao", "resposta": "(sem gravação da geração para este caminho; rode em live)"}
        registro = {"node": "gerar", "tipo": "geração", "provider": model, "synthetic": False,
                    "latency_ms": out["latency_ms"], "cost_usd": cost_usd(model_id, out["tokens_in"], out["tokens_out"])}
        return {"rascunho": out["texto"], "chamadas": [registro]}

    def verificar(state: AgentState) -> dict:
        trio = {"pergunta": state["pergunta"], "dados": state["dados"], "resposta": state["rascunho"]}
        try:
            result = decidir("verificacao", trio, VERIFICACAO)
        except ReplayMissError:
            return {"desfecho": "sem_gravacao", "resposta": state["rascunho"]}
        p = {k: float(v.value) for k, v in result.answers.items()}
        minimo = limiares["verificacao_minima"]
        ok = p.get("responde_pedido", 0) >= minimo and p.get("inventa_numero", 1) < minimo and p.get("segue_politica", 0) >= minimo
        return {"desfecho": "aprovada" if ok else "reprovada",
                "resposta": state["rascunho"] if ok else MSG_REPROVADA,
                "chamadas": [_registro("verificacao", result)]}

    def depois_de(node_ok: str):
        return lambda state: END if state.get("desfecho") else node_ok

    return (
        StateGraph(AgentState)
        .add_node("guardrail", guardrail)
        .add_node("triagem", triagem)
        .add_node("consulta", consulta)
        .add_node("gerar", gerar)
        .add_node("verificar", verificar)
        .add_edge(START, "guardrail")
        .add_conditional_edges("guardrail", depois_de("triagem"), ["triagem", END])
        .add_conditional_edges("triagem", depois_de("consulta"), ["consulta", END])
        .add_edge("consulta", "gerar")
        .add_conditional_edges("gerar", depois_de("verificar"), ["verificar", END])
        .add_edge("verificar", END)
        .compile()
    )
