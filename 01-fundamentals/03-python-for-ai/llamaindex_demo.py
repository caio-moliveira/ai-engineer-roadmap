import os
from llama_index.llms.openai import OpenAI
from llama_index.core.llms import ChatMessage
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

def generate_text_llamaindex() -> str:
    """
    Exemplo simples de integração direta com LLM via LlamaIndex.
    Utiliza a abstração de LLM para gerar texto sem RAG.
    """
    try:
        # 1. Inicializa o LLM (OpenAI neste caso)
        # O LlamaIndex detecta automaticamente a OPENAI_API_KEY do ambiente
        llm = OpenAI(model="gpt-4.1-mini", temperature=0.7)
        prompt = "Por que Python é a melhor linguagem de programação para IA?"
        
        # 2. Realiza a chamada de completamento (complete)
        # Diferente do RAG, aqui falamos diretamente com o modelo
        response = llm.complete(prompt)
        
        return str(response)
    except Exception as e:
        return f"Erro no LlamaIndex: {e}"

def generate_text_llamaindex_messages() -> str:
    """
    Exemplo simples de integração direta com LLM via LlamaIndex.
    Utiliza a abstração de LLM para gerar texto sem RAG.
    """ 
    try:
        # 1. Inicializa o LLM (OpenAI neste caso)
        # O LlamaIndex detecta automaticamente a OPENAI_API_KEY do ambiente
        llm = OpenAI(model="gpt-4.1-mini")
        messages = [
            ChatMessage(
                role="system", content="Você é um especialista em Python."
            ),
            ChatMessage(role="user", content="Por que Python é a melhor linguagem de programação para IA?"),
        ]   
        
        # 2. Realiza a chamada de completamento (complete)
        # Diferente do RAG, aqui falamos diretamente com o modelo
        response = llm.chat(messages)
        
        return str(response)
    except Exception as e:
        return f"Erro no LlamaIndex: {e}"

if __name__ == "__main__":
    # Teste simples
    # resultado = generate_text_llamaindex()
    # print("Resposta LlamaIndex:", resultado)

    resultado = generate_text_llamaindex_messages()
    print("Resposta LlamaIndex:", resultado)
