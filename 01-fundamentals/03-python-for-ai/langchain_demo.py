import os
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

def generate_text_langchain(topic: str) -> str:
    """
    Exemplo simples de integração com LangChain.
    Usa LCEL (LangChain Expression Language) para criar uma chain básica.
    """
    # 1. Inicializa o modelo de chat
    model = ChatOpenAI(
        model="gpt-4.1-mini",
        api_key=os.getenv("OPENAI_API_KEY")
    )
    
    # 2. Define o template do prompt
    prompt = ChatPromptTemplate.from_template("Dê uma dica de produtividade para: {topic}")
    
    # 3. Define o parser de saída (para converter a mensagem do AI em string)
    # output_parser = StrOutputParser()
    
    # 4. Cria a chain conectando os componentes
    chain = prompt | model 
    
    try:
        # 5. Invoca a chain
        response = chain.invoke({"topic": topic})
        return response
    except Exception as e:
        return f"Erro no LangChain: {e}"

def generate_text_langchain_messages() -> str:
    """
    Exemplo simples de integração com LangChain.
    Usa LCEL (LangChain Expression Language) para criar uma chain básica.
    """
    # 1. Inicializa o modelo de chat
    model = ChatOpenAI(
        model="gpt-4.1-mini",
        api_key=os.getenv("OPENAI_API_KEY")
    )
    
    messages = [
        (
            "system",
            "Você é um especialista em Python.",
        ),
        ("human", "Por que Python é a melhor linguagem para IA?"),
    ]
    
    try:
        # 5. Invoca a chain
        response = model.invoke(messages)
        return response
    except Exception as e:
        return f"Erro no LangChain: {e}"

if __name__ == "__main__":
    # Teste simples
    # resultado = generate_text_langchain("Python")
    # print(resultado)
    resultado = generate_text_langchain_messages()
    print(resultado)
