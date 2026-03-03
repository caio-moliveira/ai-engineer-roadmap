import uuid
from typing import Literal, TypedDict
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langgraph.types import Command, interrupt
from langgraph.graph import END, START, StateGraph
from langgraph.checkpoint.memory import InMemorySaver

# ---------- Schemas ----------
class EmailClassification(TypedDict):
    intent: Literal["question", "bug", "billing", "feature", "complex"]
    urgency: Literal["low", "medium", "high", "critical"]
    topic: str
    summary: str

class EmailAgentState(TypedDict):
    email_content: str
    sender_email: str
    email_id: str
    classification: EmailClassification | None
    ticket_id: str | None
    search_results: list[str] | None
    customer_history: dict | None
    draft_response: str | None

# ---------- NÓS ----------
def read_email(state: EmailAgentState) -> EmailAgentState:
    print(f"-> [1] Lendo E-mail: {state['email_content'][:30]}...")
    return {}

def classify_intent(state: EmailAgentState) -> EmailAgentState:
    print(f"-> [2] LLM Classificando intenções (Simulação)")
    # MOCK (para não gastar créditos OpenAI atoa)
    # Na aula o código era:
    # structured_llm = llm.with_structured_output(EmailClassification)
    # classification = structured_llm.invoke(f"Analise: {state['email_content']}")
    
    # Simularemos a resposta estruturada:
    urgency = "high" if "urgente" in state['email_content'].lower() or "dobrado" in state['email_content'].lower() else "low"
    mock_classif = EmailClassification(
        intent="bug" if "bug" in state['email_content'].lower() else "billing",
        urgency=urgency,
        topic="Suporte Financeiro",
        summary="Reclamação do cliente sobe pendências."
    )
    return {"classification": mock_classif}

def search_documentation(state: EmailAgentState) -> EmailAgentState:
    print(f"-> [3.A] Buscando Info Auxiliar na Base...")
    return {"search_results": ["Doc1: Reembolso Leva 5 dias.", "Doc2: Erros sistêmicos contatam gerente."]}

def bug_tracking(state: EmailAgentState) -> EmailAgentState:
    print(f"-> [3.B] Abrindo chamado no Jira...")
    return {"ticket_id": f"BUG-{str(uuid.uuid4())[:6]}"}

def write_response(state: EmailAgentState) -> Command[Literal["human_review", "send_reply"]]:
    print(f"-> [4] Verificando Necessidades Condicionais p/ Resposta")
    classification = state.get('classification', {})
    
    needs_review = classification.get('urgency') in ['high', 'critical']
    
    minuta = f"Prezado Cliente, sentimos muito pelo erro de faturamento referênte a '{state['email_content'][:10]}'. Processaremos o estorno. - AI"
    
    if needs_review: goto = "human_review"
    else: goto = "send_reply"

    return Command(
        update={"draft_response": minuta},
        goto=goto
    )

def human_review(state: EmailAgentState) -> Command[Literal["send_reply", END]]:
    print(f"-> [5] [!!] MODERAÇÃO ACIONADA [!!]")
    
    human_decision = interrupt({
        "email_id": state['email_id'],
        "urgency": state['classification']['urgency'],
        "draft_response": state['draft_response'],
        "alerta": "Revisão e Aprovação requeridas antes do Envio Oficial."
    })

    if human_decision.get("approved"):
        return Command(
            update={"draft_response": human_decision.get("edited_response", state['draft_response'])},
            goto="send_reply"
        )
    return Command(update={}, goto=END)

def send_reply(state: EmailAgentState) -> EmailAgentState:
    print(f"\n--> [FINAL] Enviando Email: '{state['draft_response']}'\n")
    return {}

# ---------- GRAFO ----------
builder = StateGraph(EmailAgentState)

builder.add_node("read_email", read_email)
builder.add_node("classify_intent", classify_intent)
builder.add_node("search_documentation", search_documentation)
builder.add_node("bug_tracking", bug_tracking)
builder.add_node("write_response", write_response)
builder.add_node("human_review", human_review)
builder.add_node("send_reply", send_reply)

builder.add_edge(START, "read_email")
builder.add_edge("read_email", "classify_intent")
builder.add_edge("classify_intent", "search_documentation")
builder.add_edge("classify_intent", "bug_tracking") # FANOUT Paralelo
builder.add_edge("search_documentation", "write_response") # FANIN Convergindo
builder.add_edge("bug_tracking", "write_response")
# As arestas "write_response" e "human_review" são dinâmicas via Goto()
builder.add_edge("send_reply", END)

# OBRIGATÓRIO pra Human in The Loop
memory = InMemorySaver()
app = builder.compile(checkpointer=memory)

if __name__ == "__main__":
    print("----- Iniciando Capstone Agente -----")
    # Caso 1: Teste com caso "Urgente" que baterá no moderador
    initial_state = {
        "email_content": "Fui cobrado dobrado! Isso é URGENTE e inadmissível!",
        "sender_email": "cliente-estressado@gmail.com",
        "email_id": "MSG_1020"
    }

    config = {"configurable": {"thread_id": "thread-email-10"}}
    
    print("\n--- PASSO A PASSO DA INVOCACAO 1 ---")
    result = app.invoke(initial_state, config)
    
    if '__interrupt__' in result:
        print(f"\n[SISTEMA PAUSADO] - A IA Pediu Aprovação da Minuta abaixo:")
        info_pausa = result['__interrupt__'][-1].value
        print(f"Draft: {info_pausa['draft_response']}")
        print(f"Nível: {info_pausa['urgency']}")
        
        simulando_humano = input("\n[Admin] - Aprova a Redação acima? [s/n]: ")
        
        if simulando_humano.lower() == 's':
            resposta_humana = Command(resume={"approved": True})
            print("\n--- RETOMANDO A INVOCACAO DO PONTO PAUSADO ---")
            app.invoke(resposta_humana, config)
        else:
            print("Email Rejeitado. Operador assumiu controle manual.")
