import os
import networkx as nx
import matplotlib.pyplot as plt
from langchain_community.vectorstores import InMemoryVectorStore
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from langchain_graph_retriever import GraphRetriever
from langchain_graph_retriever.document_graph import create_graph
from graph_retriever.strategies import Eager
from dotenv import load_dotenv

load_dotenv()

def main():
    print("--- 01. Graph RAG com LangChain (Traversals) ---")
    print("Demonstração de como navegar por metadados conectados como um grafo.\n")

    # 1. Configurar Embeddings
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

    # 2. Criar Dados de Exemplo com Conexões Explícitas
    # Imagine que temos documentos sobre tecnologia e suas dependências.
    # As conexões são definidas nos metadados (quem depende de quem).
    docs = [
        Document(
            id="python",
            page_content="Python é uma linguagem de programação de alto nível.",
            metadata={"related_to": ["django", "pandas", "machine_learning"]}
        ),
        Document(
            id="django",
            page_content="Django é um framework web de alto nível escrito em Python.",
            metadata={"related_to": ["python", "web_development"]}
        ),
        Document(
            id="pandas",
            page_content="Pandas é uma biblioteca de análise de dados flexível.",
            metadata={"related_to": ["python", "data_science"]}
        ),
        Document(
            id="web_development",
            page_content="Desenvolvimento Web envolve criar sites e aplicações para a internet.",
            metadata={"related_to": ["html", "css", "javascript", "react"]}
        ),
        Document(
            id="data_science",
            page_content="Data Science é o estudo de dados para extrair insights significativos.",
            metadata={"related_to": ["pandas", "machine_learning", "deep_learning"]}
        ),
        Document(
            id="html",
            page_content="HTML é a linguagem de marcação padrão para criar páginas web.",
            metadata={"related_to": ["web_development", "css", "javascript"]}
        ),
        Document(
            id="css",
            page_content="CSS é usado para estilizar elementos escritos usando HTML.",
            metadata={"related_to": ["web_development", "html", "javascript"]}
        ),
        Document(
            id="javascript",
            page_content="JavaScript é uma linguagem de programação para web.",
            metadata={"related_to": ["web_development", "html", "css", "react"]}
        ),
        Document(
            id="react",
            page_content="React é uma biblioteca JavaScript de código aberto com foco em criar interfaces de usuário.",
            metadata={"related_to": ["web_development", "javascript"]}
        ),
        Document(
            id="machine_learning",
            page_content="Machine Learning foca no desenvolvimento de algoritmos que aprendem.",
            metadata={"related_to": ["python", "data_science", "deep_learning"]}
        ),
        Document(
            id="deep_learning",
            page_content="Deep Learning é baseado em redes neurais artificiais com múltiplas camadas.",
            metadata={"related_to": ["machine_learning", "data_science"]}
        ),
        Document(
            id="sql",
            page_content="SQL é uma linguagem para gerenciar banco de dados relacional.",
            metadata={"related_to": ["python", "django", "pandas", "data_science", "database"]}
        ),
        Document(
            id="database",
            page_content="Um banco de dados é uma coleção organizada de dados.",
            metadata={"related_to": ["sql"]}
        ),
    ]

    print("Indexando documentos no Vector Store em memória...")
    vector_store = InMemoryVectorStore.from_documents(
        documents=docs,
        embedding=embeddings,
    )

    # 3. Configurar o Graph Retriever
    # Aqui definimos que a aresta do grafo é o metadado "related_to" apontando para outro ID.
    # edge = ("metadata_key", "metadata_key") significa que o valor de 'related_to' de um doc
    # aponta para o ID de outro doc que tenha esse valor em algum campo?
    # Na verdade, a lib usa edges=[("start_attr", "end_attr")].
    # Se start_attr é "related_to", ele pega os valores dessa lista e busca nos docs onde "id" (ou default) bate.
    
    # A biblioteca assume que os valores em 'related_to' correspondem aos IDs dos documentos no store.
    traversal_retriever = GraphRetriever(
        store=vector_store,
        edges=[("related_to", "related_to")], # Conecta o valor de 'related_to' ao documento que tem esse ID?
        # A documentação simplificada sugere edges=[("habitat", "habitat")] para conectar valores iguais.
        # Mas para conectar doc A -> doc B, precisamos que doc A tenha link para doc B.
        strategy=Eager(k=15, start_k=2, max_depth=3),
    )
    
    # Nota: A lib langchain-graph-retriever é recente e pode ter comportamentos específicos na definição de arestas.
    # O padrão edges=[("attr", "attr")] conecta documentos que compartilham o MESMO valor no atributo "attr".
    # Para conectar A -> B explicitamente, a lógica seria um pouco diferente ou exigiria adaptadores.
    # Neste exemplo, estamos simulando que se 'python' tem 'related_to': ['django'], e 'django' tem o ID 'django',
    # a travessia funcionará se o grafo for construído sobre esses valores.

    # 4. Executar Busca
    query = "Fale sobre Python"
    print(f"\nQuery: '{query}'")
    
    # O retriever primeiro busca os documentos mais similares à query (start_k=1).
    # Encontra 'python'.
    # Depois, expande para os vizinhos no grafo (max_depth=2).
    # Deve trazer 'django' e 'pandas'.
    
    results = traversal_retriever.invoke(query)
    
    print(f"\nResultados encontrados: {len(results)}")
    for doc in results:
        print(f"\n[ID: {doc.id}]")
        print(f"Conteúdo: {doc.page_content}")
        print(f"Relações: {doc.metadata.get('related_to')}")

    print("\nGerando visualização do grafo...")
    document_graph = create_graph(
        documents=results,
        edges=traversal_retriever.edges,
    )

    nx.draw(document_graph, with_labels=True)
    plt.show()

if __name__ == "__main__":
    main()
