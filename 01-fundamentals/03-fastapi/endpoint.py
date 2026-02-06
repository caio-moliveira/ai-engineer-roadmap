import os
from dotenv import load_dotenv

# OpenAI Imports
from openai import AsyncOpenAI

# LangChain Imports
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser


# Carrega variáveis de ambiente
load_dotenv()



# --- Funções adaptadas dos exemplos anteriores ---
async def generate_text_openai(prompt: str) -> str:
    """
    Integração direta com SDK da OpenAI (Async).
    """
    client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    try:
        response = await client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {"role": "system", "content": "Você é um especialista em Python."},
                {"role": "user", "content": prompt},
            ],
        )
        return response.choices[0].message.content
    except Exception as e:
        raise Exception(f"Erro OpenAI: {e}")

async def generate_text_langchain(topic: str) -> str:
    """
    Integração com LangChain usando LCEL.
    """
    try:
        model = ChatOpenAI(
            model="gpt-4.1-mini",
            api_key=os.getenv("OPENAI_API_KEY")
        )
        
        # Template simples
        prompt = ChatPromptTemplate.from_template("Dê uma dica de produtividade para: {topic}")
        
        # Chain: Prompt -> Model -> OutputParser
        chain = prompt | model | StrOutputParser()
        
        # Execução assíncrona
        response = await chain.ainvoke({"topic": topic})
        return response
    except Exception as e:
        raise Exception(f"Erro LangChain: {e}")