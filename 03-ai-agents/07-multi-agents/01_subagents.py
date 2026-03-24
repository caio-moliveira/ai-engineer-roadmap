import os
from dotenv import load_dotenv

from langchain.agents import create_agent, AgentState
from langchain.tools import tool
from langchain.messages import HumanMessage, ToolMessage
from langgraph.types import Command
from langchain_tavily import TavilySearch
from langchain_core.tools import InjectedToolCallId
from typing_extensions import Annotated
import pprint

load_dotenv()

class WeddingState(AgentState):
    origin: str
    destination: str
    guest_count: str
    genre: str


tavily_tool = TavilySearch(max_results=3)

# Subagente 1: Viagens
travel_agent = create_agent(
    model="gpt-4o-mini",
    tools=[tavily_tool],
    system_prompt="""Você é um agente de viagens impecável. 
    Ache o melhor voo usando a ferramenta de busca considerando a origem e destino."""
)

# Subagente 2: Espaços/Locais
venue_agent = create_agent(
    model="gpt-4o-mini",
    tools=[tavily_tool],
    system_prompt="""Você é um especialista em locais de casamento. 
    Encontre o melhor local usando a ferramenta de busca dado o número de convidados e o destino."""
)


@tool
def search_flights(origin: str, destination: str) -> str:
    """Aciona o subagente de Viagens para buscar voos considerando a origem e destino do casamento."""
    response = travel_agent.invoke({
        "messages": [HumanMessage(content=f"Ache voos de {origin} para {destination}")]
    })
    
    print("\n[travel_agent]")
    pprint.pprint(response)
    
    return response['messages'][-1].content

@tool
def search_venues(destination: str, capacity: str) -> str:
    """Aciona o subagente de Locais para achar opções no destino com a capacidade necessária."""
    response = venue_agent.invoke({
        "messages": [HumanMessage(content=f"Ache locais em {destination} para {capacity} pessoas")]
    })
    
    print("\n[venue_agent]")
    pprint.pprint(response)
    
    return response['messages'][-1].content

@tool
def update_wedding_state(origin: str, destination: str, guest_count: str, tool_call_id: Annotated[str, InjectedToolCallId]) -> Command:
    """Use ONLY when you extract the origin, destination, and guest_count from the user."""
    # O objeto Command(update={...}) altera o estado da Thread!
    print("\n[update_wedding_state]")
    print({"origin": origin, "destination": destination, "guest_count": guest_count})
    return Command(
        update={
            "origin": origin,
            "destination": destination,
            "guest_count": guest_count,
            "messages": [ToolMessage("State updated successfully", tool_call_id=tool_call_id)]
        }
    )


supervisor_agent = create_agent(
    model="gpt-4o",
    tools=[search_flights, search_venues, update_wedding_state],
    state_schema=WeddingState,
    system_prompt="""Você é o Coordenador Chefe de um Casamento.
    Sua função é APENAS delegar tarefas.
    1. Extraia a origem, destino e capacidade e use a tool 'update_wedding_state'.
    2. Em seguida, acione o 'search_flights' e o 'search_venues'.
    3. Traga um laudo final pro usuário informando o pacote completo.
    """
)

def my_subagents():
    # Execução
    question = "Oi! Sou de São Paulo. Quero casar em Paris e levar 50 convidados."
    print(f"\nQUERY: {question}")
    
    response = supervisor_agent.invoke(
        {"messages": [HumanMessage(content=question)]}
    )
    
    print("\n[supervisor_agent]")
    pprint.pprint(response)

if __name__ == "__main__":
    my_subagents()