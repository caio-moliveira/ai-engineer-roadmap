import os
import operator
from typing import Annotated, Literal, TypedDict, Any

from dotenv import load_dotenv
from pydantic import BaseModel, Field

from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
from langchain.tools import tool
from langgraph.graph import StateGraph, START, END
from langgraph.types import Send
import pprint

load_dotenv()


# ==========================================================
# 1) STATE
# ==========================================================

class AgentInput(TypedDict):
    """Input simples passado para cada subagente."""
    query: str


class AgentOutput(TypedDict):
    """Saída padronizada de cada subagente."""
    source: str
    result: Any


class Classification(TypedDict):
    """Decisão de roteamento: qual agente chamar e com qual sub-pergunta."""
    source: Literal["billing", "technical", "general"]
    query: str


class RouterState(TypedDict):
    """
    Estado principal do workflow.

    results usa reducer com operator.add para juntar resultados
    de branches paralelos.
    """
    query: str
    classifications: list[Classification]
    results: Annotated[list[AgentOutput], operator.add]
    final_answer: Any


class ClassificationResult(BaseModel):
    """Saída estruturada do classificador."""
    classifications: list[Classification] = Field(
        default_factory=list,
        description="Lista de agentes a invocar com sub-perguntas específicas.",
    )


# ==========================================================
# 2) TOOLS STUB
#    Em produção, troque por integrações reais.
# ==========================================================

@tool
def get_invoice_details(customer_id: str) -> str:
    """Busca detalhes de invoice/fatura de um cliente."""
    return (
        f"Invoice do cliente {customer_id}: plano Pro, valor USD 49.90, "
        f"status paid, vencimento 2026-03-20."
    )


@tool
def check_refund_policy(order_id: str) -> str:
    """Consulta elegibilidade de refund/reembolso."""
    return (
        f"Pedido {order_id}: elegível para reembolso parcial em até 7 dias, "
        f"desde que o consumo do serviço não tenha ultrapassado a política interna."
    )


@tool
def search_billing_faq(query: str) -> str:
    """Busca perguntas frequentes sobre cobrança."""
    return (
        f"FAQ de billing para '{query}': resultados sobre invoice, refund, "
        f"cartão recusado, upgrade, downgrade, impostos e renovação."
    )


@tool
def search_error_logs(query: str) -> str:
    """Busca logs e erros técnicos."""
    return (
        f"Logs técnicos para '{query}': ocorrências de HTTP 500 relacionadas a timeout "
        f"no serviço de pagamento e falha de retry."
    )


@tool
def search_known_incidents(query: str) -> str:
    """Busca incidentes conhecidos."""
    return (
        f"Incidentes conhecidos para '{query}': comportamento intermitente após deploy recente, "
        f"afetando autenticação de sessão e callbacks de integração."
    )


@tool
def search_technical_kb(query: str) -> str:
    """Busca artigos técnicos internos."""
    return (
        f"KB técnica para '{query}': recomenda validar token, headers, idempotência, "
        f"webhooks e tracing distribuído."
    )


@tool
def search_general_kb(query: str) -> str:
    """Busca base geral de conhecimento."""
    return (
        f"Base geral para '{query}': encontrados artigos sobre onboarding, configuração, "
        f"limites do produto e dúvidas frequentes."
    )


@tool
def search_product_docs(query: str) -> str:
    """Busca documentação funcional do produto."""
    return (
        f"Documentação do produto para '{query}': há guias de primeiros passos, "
        f"configuração inicial, planos e melhores práticas de uso."
    )


# ==========================================================
# 3) MODELOS
# ==========================================================

model = init_chat_model("openai:gpt-4.1")

# ==========================================================
# 4) HELPERS
# ==========================================================

def _extract_last_message_text(agent_result: dict) -> str:
    """
    Extrai o texto da última mensagem retornada por create_agent(...).invoke(...).
    """
    messages = agent_result.get("messages", [])
    if not messages:
        return "Nenhuma resposta retornada pelo agente."

    last_message = messages[-1]
    content = getattr(last_message, "content", "")

    if isinstance(content, str):
        return content

    if isinstance(content, list):
        parts = []
        for item in content:
            if isinstance(item, dict) and item.get("type") == "text":
                parts.append(item.get("text", ""))
            else:
                parts.append(str(item))
        return "\n".join(p for p in parts if p).strip()

    return str(content)


# ==========================================================
# 5) CLASSIFIER NODE
# ==========================================================

def classify_query(state: RouterState) -> dict:
    """
    Classifica a query e decide quais agentes chamar.
    Usa LLM com structured output.
    """
    structured_llm = model.with_structured_output(ClassificationResult)

    result = structured_llm.invoke(
        [
            {
                "role": "system",
                "content": (
                    "Você é um classificador/router de atendimento.\n\n"
                    "Sua tarefa é analisar a consulta do usuário e decidir quais agentes "
                    "especializados devem ser chamados.\n\n"
                    "Agentes disponíveis:\n"
                    "- billing: fatura, invoice, cobrança, cartão, pagamento, reembolso, plano, renovação\n"
                    "- technical: bug, erro, API, integração, falha, incidente, autenticação, deploy, performance\n"
                    "- general: dúvidas gerais de produto, onboarding, uso da plataforma, configuração e documentação funcional\n\n"
                    "Regras:\n"
                    "1. Retorne somente os agentes relevantes.\n"
                    "2. Para cada agente, gere uma sub-pergunta específica e útil para aquele domínio.\n"
                    "3. Se a consulta envolver mais de um domínio, retorne múltiplos agentes.\n"
                    "4. Evite duplicidade entre as sub-perguntas.\n"
                    "5. Se a pergunta for ampla, inclua general quando fizer sentido.\n"
                    "6. Responda estritamente no schema estruturado.\n\n"
                    "Exemplos:\n"
                    "Usuário: 'Preciso de refund porque fui cobrado em duplicidade.'\n"
                    "-> billing\n\n"
                    "Usuário: 'Minha API está retornando erro 500 após o deploy.'\n"
                    "-> technical\n\n"
                    "Usuário: 'Como troco meu plano e onde vejo minhas faturas?'\n"
                    "-> billing + general\n\n"
                    "Usuário: 'Fui cobrado depois do upgrade e minha integração falhou.'\n"
                    "-> billing + technical + general (se contexto funcional ajudar)"
                ),
            },
            {
                "role": "user",
                "content": state["query"],
            },
        ]
    )

    print("\n[classify_query]")
    print(result.model_dump() if hasattr(result, "model_dump") else result)

    classifications = result.classifications or []

    if not classifications:
        classifications = [
            {
                "source": "general",
                "query": f"Explique em termos gerais a seguinte solicitação do usuário: {state['query']}",
            }
        ]

    return {"classifications": classifications}


# ==========================================================
# 6) ROUTER -> SEND
# ==========================================================

def route_to_agents(state: RouterState) -> list[Send]:
    """
    Converte as classificações em Send(...) para execução paralela.
    """
    sends: list[Send] = []

    for classification in state["classifications"]:
        source = classification["source"]
        query = classification["query"]

        if source == "billing":
            sends.append(Send("billing_node", {"query": query}))
        elif source == "technical":
            sends.append(Send("technical_node", {"query": query}))
        elif source == "general":
            sends.append(Send("general_node", {"query": query}))

    if not sends:
        sends.append(
            Send(
                "general_node",
                {"query": f"Explique em termos gerais a seguinte solicitação: {state['query']}"},
            )
        )

    return sends


# ==========================================================
# 7) AGENT NODES
#    Cada node cria o agente dentro da própria função.
# ==========================================================

def billing_node(state: AgentInput) -> dict:
    billing_agent = create_agent(
        model=model,
        tools=[get_invoice_details, check_refund_policy, search_billing_faq],
        system_prompt=(
            "Você é um especialista de Billing Support.\n"
            "Seu foco é cobrança, invoice, faturas, cartão, renovação, imposto, "
            "upgrade/downgrade, cancelamento e refund.\n"
            "Responda com objetividade, explique políticas com clareza e diga "
            "quais dados faltariam para uma resolução definitiva quando necessário.\n"
            "Sempre que útil, use as tools disponíveis."
        ),
    )

    result = billing_agent.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": state["query"],
                }
            ]
        }
    )

    print("\n[billing_node]")
    pprint.pprint(result)


    return {
        "results": [
            {
                "source": "billing",
                "result": result,
            }
        ]
    }


def technical_node(state: AgentInput) -> dict:
    technical_agent = create_agent(
        model=model,
        tools=[search_error_logs, search_known_incidents, search_technical_kb],
        system_prompt=(
            "Você é um especialista de Technical Support.\n"
            "Seu foco é bugs, erros 4xx/5xx, logs, incidentes, integrações, APIs, "
            "deploys, autenticação, performance e troubleshooting.\n"
            "Dê diagnóstico técnico, possíveis causas, passos de validação e "
            "recomendações práticas.\n"
            "Sempre que útil, use as tools disponíveis."
        ),
    )

    result = technical_agent.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": state["query"],
                }
            ]
        }
    )

    print("\n[technical_node]")
    pprint.pprint(result)


    return {
        "results": [
            {
                "source": "technical",
                "result": result,
            }
        ]
    }


def general_node(state: AgentInput) -> dict:
    general_agent = create_agent(
        model=model,
        tools=[search_general_kb, search_product_docs],
        system_prompt=(
            "Você é um especialista General Support.\n"
            "Seu foco é dúvidas gerais sobre produto, uso da plataforma, recursos, "
            "limites, configuração básica, onboarding e documentação funcional.\n"
            "Explique de forma clara, didática e orientada ao usuário.\n"
            "Sempre que útil, use as tools disponíveis."
        ),
    )

    result = general_agent.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": state["query"],
                }
            ]
        }
    )

    print("\n[general_node]")
    pprint.pprint(result)


    return {
        "results": [
            {
                "source": "general",
                "result": result,
            }
        ]
    }


# ==========================================================
# 8) SYNTHESIS NODE
# ==========================================================

def synthesize_results(state: RouterState) -> dict:
    """
    Consolida as respostas dos agentes em uma única resposta final.
    """
    if not state.get("results"):
        return {"final_answer": "Nenhum agente retornou resultado."}

    parts = []
    for item in state["results"]:
        parts.append(
            f"Agente: {item['source']}\n"
            f"Resultado:\n{item['result']}"
        )

    synthesis_response = model.invoke(
        [
            {
                "role": "system",
                "content": (
                    "Você é o sintetizador final de um sistema multiagente.\n"
                    "Sua tarefa é consolidar as respostas dos especialistas em uma única resposta final.\n\n"
                    "Regras:\n"
                    "- Responda em português do Brasil.\n"
                    "- Seja claro, objetivo e útil.\n"
                    "- Organize em tópicos quando isso melhorar a leitura.\n"
                    "- Não repita informação sem necessidade.\n"
                    "- Se existirem lacunas, diga explicitamente o que falta.\n"
                    "- Integre billing, technical e general em uma resposta coesa.\n"
                    "- Não invente fatos além do que foi retornado pelos especialistas."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Pergunta original:\n{state['query']}\n\n"
                    f"Resultados dos especialistas:\n\n" + "\n\n---\n\n".join(parts)
                ),
            },
        ]
    )

    print("\n[synthesize_results]")
    pprint.pprint(synthesis_response.model_dump() if hasattr(synthesis_response, "model_dump") else synthesis_response)

    return {"final_answer": synthesis_response}


# ==========================================================
# 9) BUILD WORKFLOW
# ==========================================================

def build_router_workflow():
    workflow = (
        StateGraph(RouterState)
        .add_node("classify", classify_query)
        .add_node("billing_node", billing_node)
        .add_node("technical_node", technical_node)
        .add_node("general_node", general_node)
        .add_node("synthesize", synthesize_results)
        .add_edge(START, "classify")
        .add_conditional_edges(
            "classify",
            route_to_agents,
            ["billing_node", "technical_node", "general_node"],
        )
        .add_edge("billing_node", "synthesize")
        .add_edge("technical_node", "synthesize")
        .add_edge("general_node", "synthesize")
        .add_edge("synthesize", END)
        .compile()
    )

    return workflow


# ==========================================================
# 10) TESTE
# ==========================================================

def run_example(app, user_query: str):
    print(f"\nQUERY: {user_query}")

    result = app.invoke(
        {
            "query": user_query,
            "classifications": [],
            "results": [],
            "final_answer": "",
        }
    )



if __name__ == "__main__":
    if not os.getenv("OPENAI_API_KEY"):
        raise RuntimeError("OPENAI_API_KEY não encontrada.")

    app = build_router_workflow()

    exemplos = [
        "Preciso de reembolso porque fui cobrado em duplicidade.",
    ]

    for pergunta in exemplos:
        run_example(app, pergunta)