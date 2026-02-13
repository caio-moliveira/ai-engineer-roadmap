import os
from dotenv import load_dotenv
from llama_index.core import PropertyGraphIndex, SimpleDirectoryReader, Settings
from llama_index.llms.openai import OpenAI
from llama_index.embeddings.openai import OpenAIEmbedding

load_dotenv()

def main():
    print("--- 02. Graph RAG com LlamaIndex (Property Graph) ---")
    print("Construindo um Grafo de Propriedades a partir de documentos e buscando com contexto.\n")

    # 1. Configurações
    Settings.llm = OpenAI(model="gpt-4o-mini", temperature=0)
    Settings.embed_model = OpenAIEmbedding(model="text-embedding-3-small")

    # 2. Carregar Documentos
    # Usaremos um texto simples para demonstração rápida
    from llama_index.core import Document
    docs = [
        Document(text="Elon Musk é o CEO da SpaceX e da Tesla. A SpaceX foi fundada em 2002."),
        Document(text="A Tesla produz carros elétricos e baterias. Sua sede é no Texas."),
        Document(text="A Starship é um foguete desenvolvido pela SpaceX para missões a Marte."),
    ]

    print("Indexando documentos no Property Graph Index (extraindo entidades e relações)...")
    # O PropertyGraphIndex usa o LLM para extrair automaticamente nós (entidades) e arestas (relações)
    # e armazena tanto a estrutura do grafo quanto os embeddings dos vetores.
    index = PropertyGraphIndex.from_documents(
        docs,
        embed_model=Settings.embed_model,
        kg_extractors=[], # Usa extratores padrão (implícitos) ou vazios para começar simples
        show_progress=True
    )

    # 3. Configurar o Retriever
    print("\nConfigurando Retriever...")
    # O retriever pode buscar por similaridade vetorial nos nós do grafo, 
    # ou usar a estrutura para expandir a busca.
    retriever = index.as_retriever(
        include_text=True, # Inclui o texto original dos chunks associados
    )

    # 4. Executar Busca
    query = "O que a empresa de Elon Musk produz?"
    print(f"\nQuery: '{query}'")
    
    nodes = retriever.retrieve(query)

    print(f"\nResultados encontrados: {len(nodes)}")
    for i, node in enumerate(nodes):
        print(f"\n[{i+1}] Texto: {node.text}")
        # Em implementações reais de KG, teríamos acesso aos triplets extraídos.
        # Aqui, o PropertyGraphIndex ancora os triplets de volta ao texto.

    print("\nNota: O PropertyGraphIndex é a forma moderna e unificada de fazer Graph RAG no LlamaIndex, combinando Vector + Knowledge Graph.")

if __name__ == "__main__":
    main()
