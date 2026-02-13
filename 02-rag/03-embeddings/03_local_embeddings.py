from sentence_transformers import SentenceTransformer

def main():
    print("=== Embeddings Locais (Open Source) ===\n")
    
    # Por que rodar localmente?
    # 1. Privacidade total (dados não saem da sua máquina).
    # 2. Custo zero (apenas eletricidade/CPU).
    # 3. Sem latência de rede.
    
    # Modelo Escolhido: 'all-MiniLM-L6-v2'
    # É um modelo pequeno, muito rápido e com ótima qualidade para inglês.
    # Para Português, modelos como 'multilingual-e5-base' são recomendados.
    nome_modelo = 'all-MiniLM-L6-v2' 
    
    print(f"Carregando modelo: {nome_modelo}...")
    print("(A primeira vez pode demorar pois fará o download da internet)")
    
    # 1. Inicializa o Modelo
    model = SentenceTransformer(nome_modelo)
    
    # 2. Lista de frases para transformar em vetores
    frases = [
        "A inteligência artificial é fascinante",
    ]
    
    # 3. Geração dos Embeddings
    print(f"\nGerando embeddings para {len(frases)} frases...")
    embeddings = model.encode(frases)
    
    # 4. Resultados
    for i, frase in enumerate(frases):
        vetor = embeddings[i]
        print(f"\nFrase: '{frase}'")
        print(f"Tamanho do Vetor: {len(vetor)}") # Geralmente 384 para MiniLM
        print(f"Primeiros 3 valores: {vetor[:3]}")

if __name__ == "__main__":
    main()
