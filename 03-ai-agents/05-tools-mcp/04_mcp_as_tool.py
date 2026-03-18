import asyncio
import os
import sys
import pprint
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from langchain.agents import create_agent

# Usando o adaptador oficial Langchain como pedido
from langchain_mcp_adapters.client import MultiServerMCPClient

load_dotenv()

async def main():
    print("Iniciando o Exemplo 04: MCP como Tool (Cliente)\n")
    print("Usaremos o MultiServerMCPClient para englobar as tools expostas em 03_mcp_server.py.")
    
    server_script = os.path.join(os.path.dirname(__file__), "03_mcp_server.py")
    
    # O MultiServerMCPClient gerencia as conexões de múltiplos servidores de forma asynche
    # via StdioServerParameters ou HTTP. O construtor context manager lidará com sub-processos.
        
    print("Conectando ao Travel_MCP Server... (Subprocess)")
    # Inicia e amarra um servidor stdio dinamicamente
    client=MultiServerMCPClient(
        {
            "Travel_MCP": {
                "transport": "stdio",
                "command": "python",
                "args": [server_script]
            }
        }
    )
        
    # Puxando só as tools
    langchain_tools = await client.get_tools()
    print(f"[{len(langchain_tools)} Tools Descobertas e Adaptadas]")
    for t in langchain_tools:
        print(f" - {t.name}")
            
    print("\nCriando o Agente (create_agent)...")
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    agent = create_agent(llm, langchain_tools)
        
    # Input isolado conforme pedido
    raw_input = """O cliente pediu 7 dias em Paris, visitando a Torre Eiffel, o Arco do Triunfo, a Catedral de Notre-Dame, o Louvre, o Musée d'Orsay, o Jardim de Luxemburgo e o Jardim das Tulherias.
    A viagem será do dia 10 ao dia 17 de Maio. Use a tool create_itinerary para criar o roteiro corporativo."""
    print(f"Usuário Manual: '{raw_input}'\n")
        
    response = await agent.ainvoke(
        {"messages": [HumanMessage(content=raw_input)]}
    )

    print("\n[Resposta Final do LLM RAW]:")   
    pprint.pprint(response) 
    print("\n[Resposta Final do LLM]:")
    print(response["messages"][-1].content)

if __name__ == "__main__":
    asyncio.run(main())
