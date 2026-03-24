import os
from dotenv import load_dotenv

from langchain.agents import create_agent, AgentState
from langchain.tools import tool, ToolRuntime
from langchain.messages import HumanMessage, ToolMessage
from langgraph.types import Command
import pprint

load_dotenv()

# ==========================================
# 1. Definindo o Estado (Memória Compartilhada)
# ==========================================
class WeddingState(AgentState):
    origin: str
    destination: str
    guest_count: str
    genre: str

# ==========================================
# 2. Definindo os Subagentes (Worker Agents)
# ==========================================
# Agentes menores focados em uma única tarefa com prompts altamente especializados.
# Em produção, usariam Tools reais (ex: Tavily, RAG, SQLDatabase), 
# Aqui simularemos as respostas para focar na Orquestração.

@tool
def web_search_mock(query: str) -> str:
    """Busca simulada na web"""
    print("\n[web_search_mock]")
    print({"query": query})
    return f"Resultados para '{query}': Excelentes opções encontradas."

# Subagente 1: Viagens
travel_agent = create_agent(
    model="gpt-4o-mini",
    tools=[web_search_mock],
    system_prompt="""Você é um agente de viagens impecável. 
    Ache o melhor voo usando a tool web_search_mock considerando a origem e destino."""
)

# Subagente 2: Espaços/Locais
venue_agent = create_agent(
    model="gpt-4o-mini",
    tools=[web_search_mock],
    system_prompt="""Você é um especialista em locais de casamento. 
    Encontre o melhor local dado o número de convidados e o destino."""
)

# ==========================================
# 3. Empacotando Subagentes como "Tools" para o Supervisor
# ==========================================
# Usamos o decorator @tool e injetamos o State (usando ToolRuntime do LangGraph Custom)

@tool
def search_flights(runtime: ToolRuntime) -> str:
    """Aciona o subagente de Viagens para buscar voos considerando a origem e destino do casamento."""
    origin = runtime.state.get("origin", "Desconhecida")
    destination = runtime.state.get("destination", "Desconhecido")
    
    response = travel_agent.invoke({
        "messages": [HumanMessage(content=f"Ache voos de {origin} para {destination}")]
    })
    
    print("\n[travel_agent]")
    pprint.pprint(response)
    
    return response['messages'][-1].content

@tool
def search_venues(runtime: ToolRuntime) -> str:
    """Aciona o subagente de Locais para achar opções no destino com a capacidade necessária."""
    destination = runtime.state.get("destination", "Desconhecido")
    capacity = runtime.state.get("guest_count", "0")
    
    response = venue_agent.invoke({
        "messages": [HumanMessage(content=f"Ache locais em {destination} para {capacity} pessoas")]
    })
    
    print("\n[venue_agent]")
    pprint.pprint(response)
    
    return response['messages'][-1].content

@tool
def update_wedding_state(origin: str, destination: str, guest_count: str, runtime: ToolRuntime) -> str:
    """Use ONLY when you extract the origin, destination, and guest_count from the user."""
    # O objeto Command(update={...}) altera o estado da Thread!
    print("\n[update_wedding_state]")
    print({"origin": origin, "destination": destination, "guest_count": guest_count})
    return Command(
        update={
            "origin": origin,
            "destination": destination,
            "guest_count": guest_count,
            "messages": [ToolMessage("State updated successfully", tool_call_id=runtime.tool_call_id)]
        }
    )

# ==========================================
# 4. Agent Principal (Supervisor/Coordenador)
# ==========================================

supervisor_agent = create_agent(
    model="gpt-4o", # O Supervisor geralmente é um modelo mais "inteligente" (GPT-4o) para raciocinar
    tools=[search_flights, search_venues, update_wedding_state],
    state_schema=WeddingState, # Injetamos o Schema para habilitar a alteração do 'Command'
    system_prompt="""Você é o Coordenador Chefe de um Casamento.
    Sua função é APENAS delegar tarefas.
    1. Extraia a origem, destino e capacidade e use a tool 'update_wedding_state'.
    2. Em seguida, acione o 'search_flights' e o 'search_venues'.
    3. Traga um laudo final pro usuário informando o pacote completo.
    """
)


def test_subagents():
    # Execução
    question = "Oi! Sou de São Paulo. Quero casar em Paris e levar 50 convidados."
    print(f"\nQUERY: {question}")
    
    response = supervisor_agent.invoke(
        {"messages": [HumanMessage(content=question)]}
    )
    
    print("\n[supervisor_agent]")
    pprint.pprint(response)

if __name__ == "__main__":
    test_subagents()
