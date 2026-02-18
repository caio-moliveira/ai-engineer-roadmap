import os
from dotenv import load_dotenv
from openai import AsyncOpenAI
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent

# Carrega variáveis de ambiente
load_dotenv()



# --- Funções adaptadas dos exemplos anteriores ---
async def generate_text_openai(capital: str) -> str:
    """
    Integração direta com SDK da OpenAI (Async).
    """
    client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    prompt = f"Traga as seguintes informações da capital:{capital}: população, país, moeda, lingua e uma curiosidade. Traga as informações em formato JSON."
    try:
        response = await client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {"role": "system", "content": "Você é um especialista em capitais do mundo."},
                {"role": "user", "content": prompt},
            ],
        )
        return response.choices[0].message.content
    except Exception as e:
        raise Exception(f"Erro OpenAI: {e}")


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
        system_prompt="Você é um especialista em capitais do mundo. Traga as seguintes informações da capital:{capital}: população, país, moeda, lingua e uma curiosidade. Traga as informações em formato JSON."
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