from typing import List, Optional
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from langchain_classic.retrievers.self_query.base import SelfQueryRetriever
from langchain_core.structured_query import StructuredQuery
from langchain_classic.chains.query_constructor.schema import AttributeInfo
from dataclasses import dataclass
from dotenv import load_dotenv
import os

load_dotenv()

# Configuração dos Metadados
metadata_field_info = [
    AttributeInfo(
        name="num_sumula",
        description=(
            "- Número da súmula (ex.: '70'). Texto simples, sem prefixo.\n"
            "- Sempre filtre pelo número da súmula quando o usuário perguntar exclusivamente usando o número."
        ),
        type="string",
    ),
    AttributeInfo(
        name="status_atual",
        description="Status atual da súmula (ex.: 'VIGENTE', 'REVOGADA', 'ALTERADA', etc.).",
        type="string",
    ),
    AttributeInfo(
        name="data_status",
        description=("Data textual no formato 'DD/MM/AA' (string). Ex.: '07/04/14'.\n"),
        type="string",
    ),
    AttributeInfo(
        name="data_status_ano",
        description=(
            "Ano da publicação no formato 'AAAA' (integer). Ex.: '2014'.\n"
            "- Você PODE usar operadores de comparação (lt, gt, lte, gte) e igualdade (eq).\n"
            "- Para anos (ex.: 'antes de 2010'), interprete como comparações sobre datas, mesmo que o campo seja string.\n"
            "- Se o usuário disser 'antes de AAAA', use 'lt' e considere o começo do ano AAAA como limite.\n"
            "- Se o usuário disser 'depois de AAAA', use 'gt' e considere o fim do ano AAAA como limite.\n"
        ),
        type="integer",
    ),
    AttributeInfo(
        name="pdf_name",
        description="Nome do arquivo PDF de origem (ex.: 'Sumula_70.pdf').",
        type="string",
    ),
    AttributeInfo(
        name="chunk_type",
        description="Tipo do chunk: 'conteudo_principal', 'referencias_normativas' ou 'precedentes'.",
        type="string",
    ),
    AttributeInfo(
        name="chunk_index",
        description="Índice do chunk no documento.",
        type="integer",
    ),
]

document_content_description = """
    Coleção de trechos (chunks) de súmulas do Tribunal de Contas de Minas Gerais, 
    cada uma com metadados como número (num_sumula), status (status_atual), 
    data textual (data_status, formato 'DD/MM/AA'), nome do arquivo (pdf_name) e tipo de trecho (chunk_type).
"""

@dataclass
class SelfQueryConfig:
    collection_name: str = "sumulas_jornada"
    k: int = 5

def main():
    print("--- 03. Self-Query Retriever (Súmulas TCMG) ---")
    
    # 1. Configurar Conexão Qdrant
    client = QdrantClient(host="localhost", port=6333)
    
    config = SelfQueryConfig()
    
    model = OpenAIEmbeddings(
            model="text-embedding-3-large",
        )

    vectorstore = QdrantVectorStore(
            client=client,
            collection_name=config.collection_name,
            embedding=model,
            sparse_vector_name="text-sparse",
            vector_name="text-dense",
        )

    # 2. Configurar LLM para Self-Query
    llm = ChatOpenAI(temperature=0, model="gpt-4o-mini") # Usar modelo capaz de estruturar query

    # 3. Criar Retriever
    retriever = SelfQueryRetriever.from_llm(
        llm=llm,
        vectorstore=vectorstore,
        document_contents=document_content_description,
        metadata_field_info=metadata_field_info,
        enable_limit=True,
        search_kwargs={"k": config.k},
        verbose=True  # Para ver a query estruturada gerada
    )

    # 4. Executar Query de Teste
    # Exemplo: Filtro por status e ano
    #query = "Quais súmulas estão VIGENTES e foram publicadas depois de 2010?"
    query = "O que diz a súmula 70?"
    print(f"\nQuery: '{query}'")

    structured_query: StructuredQuery = retriever.query_constructor.invoke(
        {"query": query})
    
    print(f"\n[DEBUG] Structured Query: {structured_query}")

    # Execução normal (o retriever fará o trabalho de usar a structured_query internamente)
    docs = retriever.invoke(query)

    print(f"\nResultados encontrados: {len(docs)}")
    for i, doc in enumerate(docs):
        print(f"\n[{i+1}] {doc.page_content[:150]}...")
        print(f"    Metadata: {doc.metadata}")
    
if __name__ == "__main__":
    main()
