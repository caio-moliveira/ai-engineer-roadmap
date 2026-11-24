"""O grafo em três versões. Cada uma funciona sozinha e acrescenta uma camada à anterior.

v1 · roteador de modelos
    roteador ─┬─ esclarecer ───────────────────────────────► fim
              └─ agente ─┬─ executar ─► agente   (só leitura)
                         └─ responder ──────────────────────► fim

v2 · + guardião e aprovação humana
    agente ─► guardiao ─┬─ permitir ──► executar ─► agente
                        ├─ aprovacao ─► (pausa) ─┬─ aprovada ─► executar
                        │                        └─ recusada ─► agente
                        └─ bloquear ──► agente

v3 · + juiz e cascata de modelos
    agente ─ responder ─► juiz ─┬─ entregar ─────────────────► fim
                                ├─ aviso (baixa confiança) ──► fim
                                └─ refazer ─► roteador (modelo grande)
"""

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph

from nodes import agente, aprovacao, esclarecer, executar, guardiao, juiz, roteador
from state import AgentState


def depois_do_roteador(state: AgentState) -> str:
    return "esclarecer" if state.get("status") == "esclarecimento" else "agente"


def build_graph(versao: str, checkpointer=None):
    """Monta e compila o grafo da versão pedida (v1, v2 ou v3)."""
    tem_guardiao = versao in ("v2", "v3")
    tem_juiz = versao == "v3"

    def depois_do_agente(state: AgentState) -> str:
        if state.get("proposta"):
            return "guardiao" if tem_guardiao else "executar"
        return "juiz" if tem_juiz else END

    g = StateGraph(AgentState)
    g.add_node("roteador", roteador)
    g.add_node("esclarecer", esclarecer)
    g.add_node("agente", agente)
    g.add_node("executar", executar)

    g.add_edge(START, "roteador")
    g.add_conditional_edges("roteador", depois_do_roteador, ["esclarecer", "agente"])
    g.add_edge("esclarecer", END)
    g.add_edge("executar", "agente")

    destinos_do_agente = ["executar", END]

    if tem_guardiao:
        g.add_node("guardiao", guardiao)
        g.add_node("aprovacao", aprovacao)
        destinos_do_agente.append("guardiao")
        g.add_conditional_edges(
            "guardiao",
            lambda s: {"permitir": "executar", "aprovacao": "aprovacao"}.get(s["decisao_guardiao"], "agente"),
            ["executar", "aprovacao", "agente"],
        )
        g.add_conditional_edges(
            "aprovacao", lambda s: "executar" if s.get("aprovado") else "agente", ["executar", "agente"]
        )

    if tem_juiz:
        g.add_node("juiz", juiz)
        destinos_do_agente.append("juiz")
        g.add_conditional_edges(
            "juiz", lambda s: "roteador" if s["decisao_juiz"] == "refazer" else END, ["roteador", END]
        )

    g.add_conditional_edges("agente", depois_do_agente, destinos_do_agente)

    # O checkpointer guarda o estado entre a pausa e a aprovação humana (interrupt).
    return g.compile(checkpointer=checkpointer or InMemorySaver())
