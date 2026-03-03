import os
from pprint import pprint
from dotenv import load_dotenv

from langchain_core.tools import tool
from langchain.agents import create_agent

load_dotenv()

# ==========================================
# 1. Definindo Tools Customizadas
# ==========================================

# A forma mais simples de criar uma ferramenta é usando o decorator @tool
# A tipagem (float) e a Docstring ("""...""") são OBRIGATÓRIAS. 
# É através da Docstring que a IA sabe O QUE essa ferramenta faz.
@tool
def square_root(x: float) -> float:
    """Calcula a raiz quadrada de um número."""
    print(f"\n[🔧 Tool Executada] -> square_root chamada com x={x}")
    return x ** 0.5

# Você pode customizar o NOME da tool que será exposto para a LLM,
# independente do nome real da função Python.
@tool("get_weather", description="Obtém o clima atual de uma localidade específica (mock).")
def fetch_weather_api(location: str) -> str:
    print(f"\n[🔧 Tool Executada] -> get_weather chamada com location={location}")
    if "são paulo" in location.lower():
        return "25°C e Nublado"
    return "Ensolarado e 30°C"


# Você pode agregar todas em uma lista
tools = [square_root, fetch_weather_api]

def test_agent_with_tools():
    print("\n" + "="*50)
    print(" INICIALIZANDO AGENTE COM TOOLS (Python Nativo)")
    print("="*50)
    
    # 2. Instanciando Agente
    agent = create_agent(
        model="gpt-4o-mini", 
        tools=tools,
        system_prompt="Você é um assistente útil. Resolva problemas matemáticos e forneça o clima usando suas ferramentas."
    )
    
    # 3. Testando Clima
    print("\n[Usuário]: Como está o clima em São Paulo hoje?")
    response = agent.invoke({
        "messages": [HumanMessage(content="Como está o clima em São Paulo hoje?")]
    })
    
    print(f"\n[Agente]: {response['messages'][-1].content}")
    
    # 4. Testando Matemática
    print("\n[Usuário]: Qual é a raiz quadrada de 467?")
    response_math = agent.invoke({
        "messages": [HumanMessage(content="Qual é a raiz quadrada de 467?")]
    })
    
    print(f"\n[Agente]: {response_math['messages'][-1].content}")
    
    # Mostrando a 'prova' de que a ToolCall ocorreu na estrutura de mensagens
    print("\n--- Inspecionando a ToolCall (Visão Backend) ---")
    for msg in response_math["messages"]:
        # Se for a mensagem do AI requisitando o uso da ferramenta:
        if hasattr(msg, 'tool_calls') and msg.tool_calls:
            print(f"Requisição da LLM: {msg.tool_calls}")


if __name__ == "__main__":
    if not os.getenv("OPENAI_API_KEY"):
        print("AVISO: A variável de ambiente OPENAI_API_KEY não foi encontrada.")
    else:
        test_agent_with_tools()
