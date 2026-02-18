import os
from openai import OpenAI
from dotenv import load_dotenv

# Carrega variáveis de ambiente (como OPENAI_API_KEY)
load_dotenv()

def generate_text_openai() -> str:
    """
    Exemplo simples de integração com a API da OpenAI.
    Recebe um prompt e retorna a resposta do modelo.
    """
    # Inicializa o cliente OpenAI
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    try:
        # Faz a chamada para a API de Chat Completion
        response = client.responses.create(
            model="gpt-5.2",
            instructions="Você é um especialista em Python.",
            input="Explique porque Python é a melhor linguagem de programação para IA.",
        )
        
        # Retorna o conteúdo da primeira escolha
        print(response.output_text)
    except Exception as e:
        print(f"Erro ao chamar OpenAI: {e}")

def generate_text_chatcompletions() -> str:
    """
    Exemplo simples de integração com a API da OpenAI.
    Recebe um prompt e retorna a resposta do modelo.
    """
    # Inicializa o cliente OpenAI
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    try:
        # Faz a chamada para a API de Chat Completion
        completion = client.chat.completions.create(
            model="gpt-5.2",
            messages=[
                {"role": "developer", "content": "Você é um especialista em Python."},
                {
                    "role": "user",
                    "content": "Explique porque Python é a melhor linguagem de programação para IA.",
                },
            ],
        )
        
        # Retorna o conteúdo da primeira escolha
        print(completion)
    except Exception as e:
        print(f"Erro ao chamar OpenAI: {e}")


if __name__ == "__main__":
    # Teste simples
    generate_text_chatcompletions()
    # generate_text_openai()
