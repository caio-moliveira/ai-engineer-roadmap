import os
from dotenv import load_dotenv
from llama_index.core import SummaryIndex, SimpleDirectoryReader, Settings
from llama_index.llms.openai import OpenAI

load_dotenv()

def main():
    print("--- 02. Summary Retrieval (LlamaIndex) ---")
    print("Objetivo: Demonstrar o modo 'llm' onde o modelo seleciona o contexto.\n")

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
    # Para demonstração, vamos usar apenas os primeiros 5 documentos para não estourar contexto/custo
    documents = documents[:5] 
    print(f"Usando {len(documents)} documentos para o índice de resumo.")

    # 3. Criar Summary Index (Index de Lista)
    # Este índice armazena os nós como uma lista sequencial.
    summary_index = SummaryIndex.from_documents(documents)

    # 4. Configurar Retriever com modo 'llm'
    # O modo 'llm' faz com que o SummaryIndex use o LLM para decidir quais nós são relevantes.
    # Isso é útil quando a busca semântica falha ou quando precisamos de uma "leitura" do conteúdo.
    retriever = summary_index.as_retriever(
        retriever_mode="llm",
        choice_batch_size=5 # Processa 5 nós por vez
    )

    # 5. Executar Busca
    # Note que esta busca é mais lenta e custosa pois envolve chamadas ao LLM para filtrar
    query = "O que o texto diz sobre o efeito estufa na introdução?"
    print(f"\nQuery: '{query}'")
    print("Processando... (Isso usa o LLM para ler os chunks e selecionar)")

    nodes = retriever.retrieve(query)

    # print(f"\nResultados encontrados: {len(nodes)}")
    # for i, node in enumerate(nodes):
    #     # Score pode não existir ou ser None neste modo, dependendo da implementação
    #     print(f"\n[{i+1}] Texto: {node.node.get_content()[:200]}...")
    print(nodes)
    print("\nNota: O modo 'llm' é poderoso para perguntas que exigem raciocínio sobre o texto, mas não escala bem para muitos documentos.")

if __name__ == "__main__":
    main()
