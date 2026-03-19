import asyncio
import os
import sys
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

from langchain_mcp_adapters.client import MultiServerMCPClient


load_dotenv()

async def main():
    print("Iniciando o Exemplo 05: Consumindo MCP como Resource\n")
    print("Neste exemplo, o agente não usa ferramentas. Ele apenas lê um texto (Resource)\n"
          "hospedado no Servidor MCP e injeta isso diretamente no seu prompt de sistema.\n")
    
    server_script = os.path.join(os.path.dirname(__file__), "03_mcp_server.py")

    print("Conectando ao Travel_MCP Server... (Subprocess)")
    client=MultiServerMCPClient(
        {
            "Travel_MCP": {
                "transport": "stdio",
                "command": "python",
                "args": [server_script]
            }
        }
    )
            
    target_uri = "travel://info/international"
    blobs = await client.get_resources("Travel_MCP", uris=[target_uri])
    policy_text = blobs[0].as_string()

    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    
    sys_msg = SystemMessage(content=f"Regras de Segurança da Agência (Contexto Injetado):\n{policy_text}")
    
    user_input = "Estou indo para Paris passar uma semana, quais cuidados devo tomar e como me preparar para essa viagem?"
    print(f"Usuário Manual: '{user_input}'\n")
    
    response = await llm.ainvoke([sys_msg, HumanMessage(content=user_input)])
    print("\n[Resposta Final do LLM Baseado Estritamente no Resource]:")
    print(response.content)

if __name__ == "__main__":
    asyncio.run(main())
