import os
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams
from dotenv import load_dotenv

load_dotenv()   

# Caminho para o PDF (ajuste se necessário)
PDF_PATH = "02-rag/05-retrievers/Understanding_Climate_Change.pdf"
COLLECTION_NAME = "climate_change_collection"

def load_and_index_pdf(reindex=False):
    """
    Carrega o PDF, divide em chunks e indexa no Qdrant local.
    Se reindex=False e a coleção existir, retorna o vectorstore existente.
    """
    
    embeddings = OpenAIEmbeddings()
    
    # Inicializa cliente Qdrant local
    client = QdrantClient(host="localhost", port=6333)
    #client = QdrantClient(path="/tmp/langchain_qdrant")
    
    # Checa se coleção existe
    collections = client.get_collections().collections
    collection_exists = any(c.name == COLLECTION_NAME for c in collections)
    
    if collection_exists and not reindex:
        print(f"--- Carregando coleção existente: {COLLECTION_NAME} ---")
        return QdrantVectorStore(
            client=client,
            collection_name=COLLECTION_NAME,
            embedding=embeddings,
        )

    print(f"--- Indexando documento: {PDF_PATH} ---")
    
    # 1. Carregar PDF
    if not os.path.exists(PDF_PATH):
        raise FileNotFoundError(f"PDF não encontrado: {PDF_PATH}")
        
    loader = PyPDFLoader(PDF_PATH)
    docs = loader.load()
    
    # 2. Split (Chunking)
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )
    splits = text_splitter.split_documents(docs)
    print(f"Criados {len(splits)} chunks.")

    # 3. Indexar no Qdrant
    # Recria coleção se forçado
    if reindex and collection_exists:
        client.delete_collection(COLLECTION_NAME)
        
    if not client.collection_exists(COLLECTION_NAME):
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(size=1536, distance=Distance.COSINE),
        )

    vectorstore = QdrantVectorStore(
        client=client,
        collection_name=COLLECTION_NAME,
        embedding=embeddings,
    )
    
    vectorstore.add_documents(splits)
    print("Indexação concluída!")
    
    return vectorstore

def get_documents_for_keyword_search():
    """
    Retorna os chunks de texto para uso no BM25 (que roda em memória).
    """
    if not os.path.exists(PDF_PATH):
        raise FileNotFoundError(f"PDF não encontrado: {PDF_PATH}")
        
    loader = PyPDFLoader(PDF_PATH)
    docs = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    return text_splitter.split_documents(docs)
