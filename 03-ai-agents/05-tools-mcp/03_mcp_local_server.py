import sys
import asyncio
from pprint import pprint
from dotenv import load_dotenv

from langchain_core.messages import HumanMessage
from langchain.agents import create_agent
from langchain_mcp_adapters.client import MultiServerMCPClient

load_dotenv()

# ==========================================
# 0. MCP (Model Context Protocol) 
# ==========================================
# O grande salto. Em vez de hardcodar @tools em Python, você conecta seu agente
# a "Servidores MCP". Um servidor MCP expõe dezenas de ferramentas através de 
# um protocolo unificado (como o HTTP faz para sites).

# Para rodar Servidores locais no Windows a partir de Subprocessos Assíncronos, 
# precisamos deste fix obrigatório:
if sys.platform == "win32":
    if not isinstance(asyncio.get_event_loop_policy(), asyncio.WindowsProactorEventLoopPolicy):
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())


async def test_local_mcp_server():
    print("\n" + "="*50)
    print(" 1. CONECTANDO AO SERVIDOR MCP LOCAL (VIA SUBPROCESSO)")
    print("="*50)
    print("O Langchain sobe e se conecta com um arquivo Python isolado...")
    print("Isso exige que 'resources/2.1_mcp_server.py' exista fisicamente.")
    print("-> *Ignoraremos a execução real desta etapa se o arquivo não existir*")
    
    # Criaremos um Mock caso o ambiente de pasta "resources" não possua o arquivo original do curso
    import os
    if not os.path.exists("resources/2.1_mcp_server.py"):
        print("\n[Aviso]: O servidor mock `resources/2.1_mcp_server.py` não foi encontrado nesta pasta.")
        print("Voltando para o modo de fallback didático.")
        return


    # 1. Configurando o Cliente MCP
    client = MultiServerMCPClient({
        "meu_servidor_local": {
            "transport": "stdio",   # STDIN e STDOUT
            "command": "python",    # Comando bash
            "args": ["resources/2.1_mcp_server.py"], # Arquivo do Servidor Secundário
        }
    })

    # 2. Puxando as Ferramentas Dinamicamente!
    # O agente não sabe QUAIS são as tools, ele pergunta pro servidor via get_tools()!
    tools = await client.get_tools()
    print(f"\n[MCP]: Servidor ofereceu {len(tools)} ferramentas.")

    # 3. Puxando Prompts de Sistema do Servidor
    # Servidores também expõem Prompts prontos (ex: "Aja como um DBA PostgreSQL...")
    raw_prompt = await client.get_prompt("meu_servidor_local", "prompt")
    system_prompt = raw_prompt[0].content
    
    agent = create_agent(
        model="gpt-4o-mini",
        tools=tools,
        system_prompt=system_prompt
    )

    print("\n[Usuário]: Fale-me sobre a library langchain-mcp-adapters")
    # Utilizamos '.ainvoke' por ser totalmente Assíncrono (I/O)
    response = await agent.ainvoke({
        "messages": [HumanMessage(content="Fale-me sobre a library langchain-mcp-adapters")]
    })
    
    print(f"\n[Agente via MCP Server]: {response['messages'][-1].content}")

if __name__ == "__main__":
    if not os.getenv("OPENAI_API_KEY"):
        print("AVISO: A variável de ambiente OPENAI_API_KEY não foi encontrada.")
    else:
        # Ponto de entrada p/ funções assíncronas do MCP
        asyncio.run(test_local_mcp_server())
