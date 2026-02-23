import os
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_qdrant import QdrantVectorStore
from qdrant_client.http.models import Distance, VectorParams

from src.qdrant_io import create_qdrant_client, get_embeddings
from src.settings import settings

MAPPING = {
    settings.QDRANT_COLLECTION_PRODUTOS: [
        "data/Guia_Produtos_Caio_Roupas_e_Tenis_1-20.pdf",
        "data/Guia_Produtos_Caio_Roupas_e_Tenis_21-40.pdf"
    ],
    settings.QDRANT_COLLECTION_SUPORTE: [
        "data/Base_de_Suporte_Caio_Roupas_e_Tenis.pdf"
    ],
    settings.QDRANT_COLLECTION_ATENDIMENTO: [
        "data/Atendimento_Especializado_Caio_Roupas_e_Tenis.pdf"
    ]
}

def load_and_index(collection_name: str, reindex: bool = False):
    client = create_qdrant_client()
    embeddings = get_embeddings()

    collections = client.get_collections().collections
    collection_exists = any(c.name == collection_name for c in collections)
    
    if collection_exists and not reindex:
        print(f"--- Coleção {collection_name} existente. Pulando indexação... ---")
        return
        
    print(f"--- Indexando documentos para: {collection_name} ---")
    
    docs = []
    for pdf_path in MAPPING.get(collection_name, []):
        if not os.path.exists(pdf_path):
            print(f"AVISO: Arquivo PDF não encontrado: {pdf_path}")
            continue
        print(f"Carregando: {pdf_path}")
        loader = PyPDFLoader(pdf_path)
        docs.extend(loader.load())
        
    if not docs:
        print(f"Nenhum documento encontrado para {collection_name}. Abortando.")
        return

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=300, chunk_overlap=0)
    splits = text_splitter.split_documents(docs)
    print(f"Criados {len(splits)} chunks para a coleção {collection_name}.")

    if reindex and collection_exists:
        client.delete_collection(collection_name)
        
    if not client.collection_exists(collection_name):
        # text-embedding-3-large tem dimensão 3072
        client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(size=3072, distance=Distance.COSINE),
        )

    vectorstore = QdrantVectorStore(
        client=client,
        collection_name=collection_name,
        embedding=embeddings,
    )
    vectorstore.add_documents(splits)
    print(f"Indexação concluída para a coleção {collection_name}!\n")

if __name__ == "__main__":
    for coll in MAPPING.keys():
        load_and_index(coll, reindex=True)
