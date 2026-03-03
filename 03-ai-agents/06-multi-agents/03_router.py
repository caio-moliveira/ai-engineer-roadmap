import os
from pprint import pprint
from typing import Literal
from dotenv import load_dotenv

from langchain_core.messages import HumanMessage
from langchain.agents import create_agent, AgentState
from langgraph.types import Command, Send

load_dotenv()

# ==========================================
# 1. Por que usar Routers? (Control Flow Direto)
# ==========================================
# Em vez de ter um "Manager" (LLM pesada) decidindo qual Tool chamar baseado 
# na conversa (Subagents pattern), o Router é um pedaço rápido (e muitas vezes
# Stateless) que pega o Input do Usuário, processa quem vai cuidar dele, 
# e ENCAMINHA para o Agente sem passar por "Tool calls" custosas.
# Isso se baseia nos comandos novos: Command(goto=...) e Send()

# Estado que irá fluir pelos Agentes (Stateless routing via Graph)
class SupportState(AgentState):
    user_query: str
    issue_type: Literal["billing", "technical", "general", "parallel_routing"]

# ==========================================
# 2. Definindo Especialistas (Nós Finais)
# ==========================================

billing_agent = create_agent(
    model="gpt-4o-mini",
    system_prompt="Você resolve B.O de faturas, reembolsos e dólares.",
    tools=[]
)

tech_support_agent = create_agent(
    model="gpt-4o-mini",
    system_prompt="Você resolve erros 500, bugs de software e logs malucos no terminal.",
    tools=[]
)

# ==========================================
# 3. O Router Classifier (Classificador Lógico)
# ==========================================
# O Router não resolve o problema. Ele APENAS roteia ou cria fanning (Send paralelo).

def route_query(state: SupportState):
    """
    Simulando a Lógica de Routing:
    - Se tem 'dollar' ou 'refund' -> vai pro Billing.
    - Se tem 'error' ou 'bug' -> vai pro Tech.
    - Se pede 'everything' -> Faz um Fan-out Paralelo prós 2 Agentes (Usando Send!)
    """
    
    query = state.get("user_query", "").lower()
    
    # Exemplo de Paralelização (Send)
    if "everything" in query:
        print("\n[🚦 Router Mágico] -> Roteando Paralelamente para Ambos (Fan-out)!")
        
        # O Send dispara N chamadas paralelas que rodarão ao mesmo tempo
        # NOTA: Em LangGraph puro, nós adicionaríamos as keys corretas pros Nodos no Graph().
        return [
            Send("billing_agent_node", {"user_query": query}),
            Send("tech_agent_node", {"user_query": query})
        ]
        
    # Exemplo de Comando Condicional Unilateral (Command - Goto)
    elif "bug" in query or "error" in query:
        print("\n[🚦 Router Lógico] -> Assunto Técnico detectado! Redirecionando (goto) Tech Support...")
        # No Grafo, estaríamos enviando a thread para o node "tech_agent_node"
        
        # SIMULAÇÃO DIDÁTICA DO GOTO DENTRO DE UM SCRIPT LINEAR:
        response = tech_support_agent.invoke({"messages": [HumanMessage(content=query)]})
        print(f"\n[Tech Agent]: {response['messages'][-1].content}")
        return Command(goto="END")
        
    elif "refund" in query or "dollars" in query:
        print("\n[🚦 Router Lógico] -> Assunto de Cobrança detectado! Redirecionando (goto) Billing Support...")
        
        response = billing_agent.invoke({"messages": [HumanMessage(content=query)]})
        print(f"\n[Billing Agent]: {response['messages'][-1].content}")
        return Command(goto="END")


def test_routers():
    print("\n" + "="*50)
    print(" INICIANDO PADRÃO ROUTERS (Command & Send)")
    print("="*50)
    
    print("\nCenário 1: Reembolso")
    print("[Usuário]: Preciso de um refund de 50 dollars")
    route_query(SupportState(user_query="Preciso de um refund de 50 dollars", messages=[]))
    
    print("\n" + "-"*50)
    
    print("\nCenário 2: Erro 500")
    print("[Usuário]: O site ta dando um error 500 no botão de checkout, que bug grave.")
    route_query(SupportState(user_query="O site ta dando um error 500 no botão de checkout, que bug grave.", messages=[]))


if __name__ == "__main__":
    if not os.getenv("OPENAI_API_KEY"):
        print("AVISO: Variável de ambiente OPENAI_API_KEY ausente.")
    else:
        test_routers()
