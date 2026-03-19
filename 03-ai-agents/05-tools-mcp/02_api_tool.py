import requests
import pprint
from dotenv import load_dotenv
from langchain.tools import tool
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from langchain.agents import create_agent

load_dotenv()

@tool
def get_weather(city: str) -> str:
    """Busca a temperatura atual de uma cidade turística usando mock fidedigno baseado em localização."""
    print(f"\n[API 1] Buscando clima para: {city}...")
    
    locations = {
        "paris": {"lat": 48.8566, "lon": 2.3522},
        "londres": {"lat": 51.5074, "lon": -0.1278},
        "sao paulo": {"lat": -23.5505, "lon": -46.6333},
        "buenos aires": {"lat": -34.6037, "lon": -58.3816}
    }
    
    loc = locations.get(city.lower())
    if not loc:
        return f"Clima para {city}: 22°C (Estimativa padrão)."
        
    url = f"https://api.open-meteo.com/v1/forecast?latitude={loc['lat']}&longitude={loc['lon']}&current_weather=true"
    try:
        data = requests.get(url, timeout=5).json()
        temp = data.get("current_weather", {}).get("temperature")
        return f"A temperatura atual em {city} é {temp}°C."
    except Exception as e:
        return f"Falha na API de clima para {city}: {e}"

@tool
def get_tourist_info(city: str) -> str:
    """Busca informações turísticas rápidas do Wikipedia para uma cidade."""
    print(f"\n[API 2] Buscando informações turísticas (Wikipedia API) para: {city}...")
    
    url = f"https://pt.wikipedia.org/api/rest_v1/page/summary/{city.capitalize()}"
    try:
        data = requests.get(url, timeout=5).json()
        return data.get("extract", f"Cidade turística famosa: {city}")
    except Exception as e:
        return f"Informação turística de {city}: Grandes monumentos, boa gastronomia."

def main():
    print("Iniciando o Exemplo 02: Tool conectada a APIs Externas (Viagens)\n")
    print("Este arquivo é focado puramente em buscar dados reais de APIs.")
    print("Não se conecta ao Exemplo 01. Variáveis providenciadas manualmente no input.\n")
    
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    agent = create_agent(llm, [get_weather, get_tourist_info])
    
    user_input = "O meu destino será Paris na data do dia 10 a 17 de maio. Como estará o clima lá e um resumo do que posso encontrar na cidade?"
    print(f"Usuário: '{user_input}'\n")
    
    print("Agente consultando APIs...\n")
    response = agent.invoke(
        {"messages": [HumanMessage(content=user_input)]}
    )
    
    print("\n[Resposta Final do LLM (Raw Struct)]:")
    pprint.pprint(response)

    print("\n[Resposta Final do LLM]:")
    print(response["messages"][-1].content)

if __name__ == "__main__":
    main()
