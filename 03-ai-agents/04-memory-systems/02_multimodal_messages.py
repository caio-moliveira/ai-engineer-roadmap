import os
import base64
from dotenv import load_dotenv

from langchain.agents import create_agent
from langchain_core.messages import HumanMessage

load_dotenv()

def test_text_input():
    print("\n" + "="*50)
    print(" PARTE 1: INPUT DE TEXTO ESTRUTURADO")
    print("="*50)
    
    # Modelo para responder com criatividade
    agent = create_agent(
        model="gpt-4o-mini", 
        tools=[], 
        system_prompt="Você é um autor de ficção científica. Descreva uma cidade capital a pedido do usuário."
    )
    
    # Formato estruturado de Input
    question = HumanMessage(content=[
        {"type": "text", "text": "Qual é a capital da Lua?"}
    ])
    
    print(f"[Usuário]: {question.content[0]['text']}")
    response = agent.invoke({"messages": [question]})
    print(f"\n[Agente Ficção]:\n{response['messages'][-1].content}")


def test_image_input():
    print("\n\n" + "="*50)
    print(" PARTE 2: INPUT DE IMAGEM (Multimodal)")
    print("="*50)
    
    image_path = "sample_image.png"
    
    if not os.path.exists(image_path):
        print(f"-> AVISO: O arquivo '{image_path}' não foi encontrado.")
        print("-> Para testar isso de verdade, crie ou coloque uma imagem PNG neste diretório com esse nome.")
        return
        
    print(f"Lendo e encodando a imagem '{image_path}'...")
    
    # Converte imagem local para Base64
    with open(image_path, "rb") as img_file:
        img_bytes = img_file.read()
        img_b64 = base64.b64encode(img_bytes).decode("utf-8")
        
    # Usa modelo multimodal
    agent = create_agent(model="gpt-4o-mini", tools=[])
    
    multimodal_question = HumanMessage(content=[
        {"type": "text", "text": "Descreva o que há nesta imagem."},
        {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{img_b64}"}}
    ])
    
    print("\n[Enviando imagem para a LLM...]")
    response = agent.invoke({"messages": [multimodal_question]})
    print(f"\n[Agente Visual]:\n{response['messages'][-1].content}")


def test_audio_input():
    print("\n\n" + "="*50)
    print(" PARTE 3: INPUT DE ÁUDIO")
    print("="*50)
    
    # Na aula isso foi feito com sounddevice gravando o mic ao vivo.
    # Em um script assíncrono, é mais seguro pedir que o usuário aponte para um wav.
    audio_path = "sample_audio.wav"
    
    if not os.path.exists(audio_path):
        print(f"-> AVISO: O arquivo de áudio '{audio_path}' não foi encontrado.")
        print("-> Crie um pequeno arquivo WAV localmente com esse nome para validar a funcionalidade.")
        return
        
    print(f"Lendo o áudio '{audio_path}'...")
    
    with open(audio_path, "rb") as aud_file:
        aud_bytes = aud_file.read()
        aud_b64 = base64.b64encode(aud_bytes).decode("utf-8")
        
    # Requer um modelo de áudio específico (gpt-4o-audio-preview)
    try:
        agent = create_agent(model="gpt-4o-audio-preview", tools=[])

        multimodal_question = HumanMessage(content=[
            {"type": "text", "text": "Crie uma transcrição ou me diga o que ouve neste arquivo de áudio."},
            {"type": "input_audio", "input_audio": {"data": aud_b64, "format": "wav"}}
        ])
        
        print("\n[Enviando áudio para a LLM...]")
        response = agent.invoke({"messages": [multimodal_question]})
        print(f"\n[Agente Auditivo]:\n{response['messages'][-1].content}")
    except Exception as e:
        print(f"\nErro ao chamar a API de áudio (Talvez sua API Key não tenha acesso a este modelo preview ainda): {e}")


if __name__ == "__main__":
    if not os.getenv("OPENAI_API_KEY"):
        print("AVISO: A variável de ambiente OPENAI_API_KEY não foi encontrada. O script não rodará corretamente.")
        
    test_text_input()
    test_image_input()
    test_audio_input()
    
    print("\n" + "="*50)
    print("Fim das demonstrações multimodais.")
    print("="*50)
