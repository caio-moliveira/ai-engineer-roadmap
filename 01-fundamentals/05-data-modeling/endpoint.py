import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from langchain.agents.structured_output import ToolStrategy
from models import CapitalData

# Carrega variáveis de ambiente
load_dotenv()


async def generate_text_langchain(capital: str) -> str:
    """
    Exemplo usando LangChain.
    """

    # modelo
    llm = ChatOpenAI(
        model="gpt-4.1-mini",
        api_key=os.getenv("OPENAI_API_KEY"),
        temperature=0.2,
    )

    # agente
    agent = create_agent(
        model=llm,
        tools=[],
        system_prompt="Você é um especialista em capitais do mundo. Traga as seguintes informações da capital:{capital}: população, país, moeda, lingua e uma curiosidade.",
        response_format=CapitalData
    )

    # invoke
    result = await agent.ainvoke(
        {
            "messages": [
                {"role": "user", "content": f"Explique sobre {capital}"}
            ]
        }
    )

    return result["messages"][-1].content