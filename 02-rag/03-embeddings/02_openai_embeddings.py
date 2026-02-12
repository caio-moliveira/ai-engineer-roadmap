import os
from openai import OpenAI
from dotenv import load_dotenv

# Carrega variáveis de ambiente do .env (recomendado para chaves API)
load_dotenv()

def main():    
    # 1. Configuração do Cliente
    # Certifique-se de ter a chave OPENAI_API_KEY no seu ambiente ou .env
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("ERRO: Chave OPENAI_API_KEY não encontrada. Configure seu .env primeiro.")
        return

    client = OpenAI(api_key=api_key)
    
    texto = "A inteligência artificial é fascinante"
    modelo = "text-embedding-3-small" # Modelo padrão, equilibrado (Custo vs Qualidade)
    
    print(f"Gerando embedding para: '{texto}'")
    print(f"Usando modelo: {modelo}...")
    
    # 2. Chamada da API
    response = client.embeddings.create(
        input=texto,
        model=modelo
    )
    
    # 3. Extraindo o Vetor
    # A resposta vem em formato JSON, precisamos pegar o valor 'embedding' do primeiro item.
    embedding_vector = response.data[0].embedding
    
    # 4. Inspecionando o Resultado
    dimensoes = len(embedding_vector)
    print(f"\nSucesso! Vetor gerado.")
    print(f"Dimensões do vetor: {dimensoes}") # Deve ser 1536 para text-embedding-3-small
    
    print(f"\nOs primeiros 5 números do vetor:")
    print(embedding_vector)
    
    # Nota sobre Custo:
    # Embeddings são muito baratos. 
    # Com $1 dólar, você pode processar ~62.500 páginas de texto (com text-embedding-3-small).
    
    # Nota sobre "Truncating" (Encurtamento):
    # O modelo 'text-embedding-3' permite pedir menos dimensões para economizar espaço no banco de dados.
    # Ex: dimensions=512
    # response = client.embeddings.create(input=texto, model=modelo, dimensions=512)

if __name__ == "__main__":
    main()
