from langchain_community.retrievers import BM25Retriever
from utils import get_documents_for_keyword_search
from nltk.tokenize import word_tokenize
import nltk



def main():
    print("--- 02. Keyword Retriever (BM25 - Busca Lexical em PDF) ---")
    print("Este método foca em palavras-chave exatas encontradas no PDF.\n")

    # 1. Carregar documentos do PDF (BM25 precisa dos textos em memória)
    try:
        docs = get_documents_for_keyword_search()
        print(f"Carregados {len(docs)} chunks para o BM25.")
    except FileNotFoundError as e:
        print(e)
        return

    # 2. Inicializando o BM25
    retriever = BM25Retriever.from_documents(docs, k=3)
    # nltk.download("punkt_tab")
    #retriever = BM25Retriever.from_documents(docs, k=3, preprocess_func=word_tokenize)   

    # 3. Buscas
    # Busca por termo específico que pode estar no texto
    query = "greenhouse gases" 
    print(f"\nQuery: '{query}'")
    results = retriever.invoke(query)
    
    print(results)
        
    print("\nNota: BM25 roda em memória. Se o PDF for gigante, cuidado com RAM.")

if __name__ == "__main__":
    main()
