import os
from dotenv import load_dotenv
from llama_index.core import TreeIndex, SimpleDirectoryReader, Settings
from llama_index.llms.openai import OpenAI

load_dotenv()

def main():
    print("--- 03. Tree Retrieval (LlamaIndex) ---")
    print("Objetivo: Demonstrar a recuperação hierárquica com Tree Index.\n")
    PDF_PATH = "Understanding_Climate_Change.pdf"
    # 1. Configurações
    Settings.llm = OpenAI(model="gpt-4o-mini", temperature=0)

    # 2. Carregar Documentos
    pdf_path = os.path.join(os.path.dirname(__file__), PDF_PATH)
    if not os.path.exists(pdf_path):
        print(f"Erro: Pasta '{pdf_path}' não encontrada.")
        return

    print("Carregando documentos...")
    documents = SimpleDirectoryReader(input_files=[pdf_path]).load_data()
    # Usando subconjunto para agilizar a construção da árvore
    documents = documents[:10]
    print(f"Construindo árvore com {len(documents)} nós iniciais...")

    # 3. Criar Tree Index
    # O TreeIndex constrói uma árvore hierárquica de nós, resumindo blocos de texto.
    # A raiz contém resumo dos filhos, e assim por diante.
    tree_index = TreeIndex.from_documents(documents)
    print("Árvore construída!")

    # 4. Configurar Retriever com modo 'select_leaf_embedding' (ou 'select_leaf')
    # select_leaf_embedding: Usa embeddings para navegar na árvore até a folha mais relevante.
    # É uma busca híbrida: estrutura de árvore + similaridade.
    retriever = tree_index.as_retriever(
        retriever_mode="select_leaf_embedding"
    )

    # 5. Executar Busca
    query = "Quais são as evidências científicas das mudanças climáticas?"
    print(f"\nQuery: '{query}'")
    
    nodes = retriever.retrieve(query)

    print(f"\nResultados encontrados: {len(nodes)}")
    for i, node in enumerate(nodes):
        print(f"\n[{i+1}] Texto: {node.node.get_content()[:200]}...")
    
    print("\nNota: O Tree Index é excelente para navegar em documentos longos e complexos, permitindo buscas que descem do geral para o específico.")

if __name__ == "__main__":
    main()
