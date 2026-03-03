import sys
import asyncio
from pprint import pprint
from dotenv import load_dotenv

from langchain_core.messages import HumanMessage
from langchain.agents import create_agent
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.checkpoint.memory import InMemorySaver

load_dotenv()

# ==========================================
# 0. MCP Servers (Remotos e Globais)
# ==========================================
# Enquanto a Aula 3 abordava servidores Python locais subindo em nossa máquina,
# o poder do MCP está em conectar sua LLM a servidores online REST 
# (via SSE - Server Sent Events) ou binários globais via uvx/npx.

# Windows asyncio fix:
if sys.platform == "win32":
    if not isinstance(asyncio.get_event_loop_policy(), asyncio.WindowsProactorEventLoopPolicy):
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

async def test_mcp_time_server():
    print("\n" + "="*50)
    print(" 1. CONECTANDO AO SERVIDOR UVX (MCP GLOBAL DE TEMPO)")
    print("="*50)
    print("Requisito: Ter o utilitário 'uvx' (ou 'npx') instalado no SO.")
    print("-> Se não tiver uvx, este comando falhará, mas a teoria permanece.\n")
    
    try:
        client = MultiServerMCPClient({
            "time_server": {
                "transport": "stdio",
                "command": "uvx",
                "args": [
                    "mcp-server-time",
                    "--local-timezone=America/Sao_Paulo" # Ajustando GMT
                ]
            }
        })
        
        tools = await client.get_tools()
        print(f"[MCP]: O Servidor de Tempo enviou {len(tools)} ferramentas.")
        
        agent = create_agent(
            model="gpt-5-nano",  # Ou qualquer LLM atual
            tools=tools,
        )
        
        print("\n[Usuário]: Que horas são?")
        response = await agent.ainvoke({
            "messages": [HumanMessage(content="Que horas são no Timezone atual do meu servidor?")]
        })
        
        print(f"\n[Agente do Tempo]: {response['messages'][-1].content}")
    
    except Exception as e:
        print(f"Erro ao testar o servidor UVX (Possivelmente uvx não instalado): {e}")


async def test_mcp_online_rest():
    print("\n\n" + "="*50)
    print(" 2. CONECTANDO AO SERVIDOR TRAVEL DA KIWI (HTTPS/SSE)")
    print("="*50)
    
    # Diferente do 'stdio', a gente não roda um shell.
    # Nós assinamos (stream) um stream HTTP de um parceiro oficial MCP na web!
    try:
        client = MultiServerMCPClient({
            "travel_server": {
                "transport": "streamable_http",
                "url": "https://mcp.kiwi.com"
            }
        })
        
        tools = await client.get_tools()
        print(f"[MCP]: A API REST da Kiwi disponibilizou {len(tools)} ferramentas de Travel.")
        
        # Como Travel é um loop complexo, passamos Memory também!
        agent = create_agent(
            model="gpt-4o-mini",
            tools=tools,
            checkpointer=InMemorySaver(),
            system_prompt="Você é um agente de viagens sênior. Responda diretamente e sem followups."
        )
        
        config = {"configurable": {"thread_id": "viagem_caio_01"}}
        
        print("\n[Usuário]: Encontre um voo direto de San Francisco para Tóquio no dia 31 de Março.")
        response = await agent.ainvoke(
            {"messages": [HumanMessage(content="Encontre um voo direto de San Francisco para Tóquio no dia 31 de Março.")]},
            config
        )
        
        print(f"\n[Travel Agent]: {response['messages'][-1].content}")
        
    except Exception as e:
        print(f"Erro ao testar a API Kiwi (Pode estar temporariamente inacessível): {e}")


if __name__ == "__main__":
    if not os.getenv("OPENAI_API_KEY"):
        print("AVISO: A variável de ambiente OPENAI_API_KEY não foi encontrada.")
    else:
        async def main():
            await test_mcp_time_server()
            await test_mcp_online_rest()
            
        asyncio.run(main())
