import asyncio
import os
import sys
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

from langchain_mcp_adapters.client import MultiServerMCPClient

load_dotenv()

async def main():
    print("Iniciando o Exemplo 06: Cliente consumindo MCP como Prompt\n")
    print("O Prompt de Geração de Roteiro é hospedado pelo MCP. O cliente passará \n"
          "as variáveis manuais pro Servidor MCP, que injetará as regras de negócio \n"
          "e devolverá o prompt 100% pronto para o LLM responder.\n")

    server_script = os.path.join(os.path.dirname(__file__), "03_mcp_server.py")

    client=MultiServerMCPClient(
        {
            "Travel_MCP": {
                "transport": "stdio",
                "command": "python",
                "args": [server_script]
            }
        }
    )
            
    prompt_name = "itinerary_planner"
    # As variáveis solicitadas que compõem a regra corporativa
    args = {
        "destination": "Paris", 
        "days": "7", 
        "profile": "Visitar pontos turísticos e culinária"
    }
    
    print(f"Solicitando Prompt Corporativo: '{prompt_name}' preenchido: {args}...\n")
    
    p_result = await client.get_prompt("Travel_MCP", prompt_name=prompt_name, arguments=args)
            
    p_result.append(HumanMessage(content="Faça o roteiro exatamente como orientado pelas regras da agência."))
    
    print("Gerando Itinerário com LLM baseado no Prompt oficial...\n")
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)
    
    res = await llm.ainvoke(p_result)
    
    print("\n[ITINERÁRIO FINAL GERADO DIRETAMENTE VIA LLM]:\n")
    print(res.content)

if __name__ == "__main__":
    asyncio.run(main())
