import os
from dotenv import load_dotenv
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Settings
from llama_index.llms.openai import OpenAI
from llama_index.embeddings.openai import OpenAIEmbedding

load_dotenv()

def main():
    print("--- 01. Vector Retrieval (LlamaIndex) ---")

    PDF_PATH = "Understanding_Climate_Change.pdf"

    # 1. Configurações Globais (LLM e Embedding)
    Settings.llm = OpenAI(model="gpt-4o-mini", temperature=0)
    Settings.embed_model = OpenAIEmbedding(model="text-embedding-3-small")

    # 2. Carregar Documentos
    # O SimpleDirectoryReader lê todos os arquivos da pasta 'data'
    pdf_path = os.path.join(os.path.dirname(__file__), PDF_PATH)
    if not os.path.exists(pdf_path):
        print(f"Erro: Pasta '{pdf_path}' não encontrada.")
        return

    print("Carregando documentos...")
    documents = SimpleDirectoryReader(input_files=[pdf_path]).load_data()
    print(f"Carregados {len(documents)} páginas/documentos.")

    # 3. Criar Index Vetorial (Em memória por padrão, ou persistido se configurado)
    # VectorStoreIndex quebra os documentos em nodes e calcula embeddings
    index = VectorStoreIndex.from_documents(documents)

    # 4. Configurar Retriever
    retriever = index.as_retriever(similarity_top_k=3)

    # 5. Executar Busca
    query = "Quais são as principais causas das mudanças climáticas?"
    print(f"\nQuery: '{query}'")
    
    nodes = retriever.retrieve(query)

    print(f"\nResultados encontrados: {len(nodes)}")
    for i, node in enumerate(nodes):
        print(f"\n[{i+1}] Score: {node.score:.4f}")
        print(f"    Texto: {node.node.get_content()}")
        print(f"    Metadata: {node.node.metadata}")
    # print(nodes)
    print("\nNota: Este retriever usa busca por similaridade de vetores (embeddings).")

if __name__ == "__main__":
    main()
