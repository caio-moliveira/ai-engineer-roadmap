from langchain.agents import create_agent
from langchain.agents.middleware import ModelFallbackMiddleware
from langchain.tools import tool
from dotenv import load_dotenv
import pprint

load_dotenv()

@tool
def consultar_politica_de_reembolso(produto: str) -> str:
    """Busca a regra corporativa de reembolso de um produto no banco de dados."""
    return f"Política do produto {produto}: O cliente tem 7 dias após a entrega para solicitar devolução."

def main():
    agente = create_agent(
        model="openai:modelo-quebrado-propositalmente",  # Forçamos um erro da API
        tools=[consultar_politica_de_reembolso],
        middleware=[
            ModelFallbackMiddleware(
                "openai:gpt-4o-mini"      
            )
        ]
    )

    resposta = agente.invoke({
        "messages": [
            {"role": "user", "content": "Olá, me explica a política de reembolso do Notebook XYZ?"}
        ]
    })
            
    ultima_mensagem = resposta['messages'][-1].content
    if not ultima_mensagem:
        # Caso o modelo decida imprimir a Tool Call direto ao invés de texto
        ultima_mensagem = f"[Uso de Ferramenta: {resposta['messages'][-1].tool_calls[0]['name']}]"

    print(f"🤖 RESPOSTA DA IA: {ultima_mensagem}\n")

    pprint.pprint(resposta)
        

if __name__ == "__main__":
    main()