import os
from dataclasses import dataclass
from dotenv import load_dotenv

from langchain.agents import create_agent
from langchain.tools import tool, ToolRuntime
from langchain.messages import HumanMessage
from pprint import pprint

load_dotenv()

# ==========================================
# 1. Definindo o Schema de Contexto
# ==========================================
# A injeção de contexto permite que ferramentas ascessem dados sem que
# a LLM precise gerá-los e sem hardcodar nas ferramentas.

@dataclass
class ColourContext:
    favourite_colour: str = "blue"
    least_favourite_colour: str = "yellow"

# ==========================================
# 2. Recebendo Contexto numa Tool (O Objeto ToolRuntime)
# ==========================================
# Usamos a anotação ToolRuntime para receber a injeção em tempo de execução
@tool
def get_favourite_colour(runtime: ToolRuntime) -> str:
    """Obtém a cor favorita do usuário"""
    print(f"\n[🔧 Tool Executada Ocultamente] -> Lendo contexto do usuário (Cor Favorita)")
    return runtime.context.favourite_colour

@tool
def get_least_favourite_colour(runtime: ToolRuntime) -> str:
    """Obtém a cor menos favorita do usuário"""
    print(f"\n[🔧 Tool Executada Ocultamente] -> Lendo contexto do usuário (Pior Cor)")
    return runtime.context.least_favourite_colour

def test_runtime_context():
    print("\n" + "="*50)
    print(" INICIALIZANDO AGENTE COM TOOL RUNTIME CONTEXT")
    print("="*50)

    # Note que no create_agent da Langchain customizada a gente passa o schema de contexto
    agent = create_agent(
        model="gpt-5-nano",
        tools=[get_favourite_colour, get_least_favourite_colour],
        context_schema=ColourContext
    )

    print("\n[Usuário]: Qual é minha cor favorita?")
    
    # Executamos passando o Objeto instanciado de contexto (ex: de um BD)
    response = agent.invoke(
        {"messages": [HumanMessage(content="Qual é minha cor favorita?")]},
        context=ColourContext()
    )
    
    print(f"\n[Agente pre-definido]: {response['messages'][-1].content}")
    
    
    print("\n-------------------------------------------")
    print("[MUDANDO O CONTEXTO PRA UM USUÁRIO DIFERENTE]")
    
    response_verde = agent.invoke(
        {"messages": [HumanMessage(content="Qual é minha cor favorita? Leia minhas preferencias")]},
        context=ColourContext(favourite_colour="green")
    )
    
    print(f"\n[Agente novo usuário]: {response_verde['messages'][-1].content}")


if __name__ == "__main__":
    if not os.getenv("OPENAI_API_KEY"):
        print("AVISO: A variável de ambiente OPENAI_API_KEY não foi encontrada.")
    else:
        test_runtime_context()
