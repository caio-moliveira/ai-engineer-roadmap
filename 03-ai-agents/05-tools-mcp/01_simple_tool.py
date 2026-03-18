import os
import pprint
from dotenv import load_dotenv
from langchain.tools import tool
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from langchain.agents import create_agent

load_dotenv()

@tool
def calculate_budget(days: int, origin: str, destination: str, date_start: str, date_end: str) -> str:
    """
    Calcula o budget (orçamento) estimado mínimo necessário para uma viagem com base nos dias e destinos.
    
    Args:
        days: Quantidade de dias da viagem (ex: 5).
        origin: Cidade de embarque (ex: São Paulo).
        destination: Cidade de destino (ex: Paris).
        date_start: Data de ida (ex: 2024-10-01).
        date_end: Data de volta (ex: 2024-10-06).
    """
    print(f"\n[TOOL EXECUTION] Calculando orçamento de {origin} para {destination} (Dias: {days})...")
    
    # Simulação de um processo determinístico simples
    base_flight_cost = 2500.0 if origin != destination else 0.0
    if "paris" in destination.lower() or "londres" in destination.lower():
        base_flight_cost += 3000.0 # Passagem internacional
        cost_per_day = 800.0
    elif "buenos aires" in destination.lower():
        base_flight_cost += 1000.0
        cost_per_day = 400.0
    else:
        cost_per_day = 250.0

    total_cost = base_flight_cost + (cost_per_day * days)
    
    return (
        f"Detalhes da Viagem:\n"
        f"Datas: {date_start} até {date_end}\n"
        f"Rota: {origin} -> {destination}\n"
        f"Dias totais: {days}\n"
        f"Passagem est.: R$ {base_flight_cost:.2f}\n"
        f"Custo diário est.: R$ {cost_per_day:.2f}/dia\n"
        f"-> Orçamento Total Recomendado: R$ {total_cost:.2f}"
    )

def main():
    print("Iniciando o Exemplo 01: Tool Simples Local (Viagens)\n")
    print("Digite os dados da viagem manualmente para testar o agente usando a tool.\n")
    
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    
    agent = create_agent(llm, [calculate_budget])
    
    # Input manual do usuário
    user_input = "Quero fazer uma viagem de São Paulo para Paris. Serão 7 dias, de 10 de maio a 17 de maio. Quanto de budget eu preciso?"
    print(f"Usuário: '{user_input}'\n")
    
    print("Agente orquestrando...\n")
    response = agent.invoke(
        {"messages": [HumanMessage(content=user_input)]}
    )
    
    print("\n[Resposta Final do LLM (Raw Struct)]:")
    pprint.pprint(response)

if __name__ == "__main__":
    main()
