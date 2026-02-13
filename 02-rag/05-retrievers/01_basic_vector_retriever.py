import os
# Importa função utilitária do 00_utils.py
from utils import load_and_index_pdf


def main():   
    # 1. Carrega (ou reusa) o índice do Qdrant com dados do PDF
    try:
        vectorstore = load_and_index_pdf()
    except FileNotFoundError as e:
        print(e)
        return

    # 2. Executando Buscas
    query = "Quais são as principais causas das mudanças climáticas?"
    print(f"\nQuery: '{query}'")

    # --- Método A: similarity_search (Direto) ---
    # Busca direta no VectorStore. Retorna lista de Documentos.
    # Útil para chamadas simples e scripts imperativos.
    print("\n--- Método A: vectorstore.similarity_search_with_score() ---")
    #opção sem score 'similarity_search'
    docs_search = vectorstore.similarity_search_with_score(query, k=3)
    for doc, score in docs_search:
        print(f"Score: {score}\n")
        print(doc)

    # --- Método B: as_retriever (Interface Runnable) ---
    # Converte o VectorStore em um componente 'Retriever'.
    # Retorna um Runnable que pode ser usado em Chains (LCEL).
    # Útil para Pipelines e Agentes.
    print("\n--- Método B: vectorstore.as_retriever() ---")
    retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
    docs_retriever = retriever.invoke(query)
    
    print(docs_retriever[0])
        
    print("\nNota: Ambos retornam o mesmo resultado, mas 'as_retriever' é melhor para integrar em Chains.")

if __name__ == "__main__":
    main()
