import os
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams
from dotenv import load_dotenv
from langfuse.langchain import CallbackHandler

# Langfuse (observability)
from langfuse import get_client, propagate_attributes

load_dotenv()

# Caminho para o PDF (ajuste se necessário)
PDF_PATH = "02-rag/05-retrievers/Understanding_Climate_Change.pdf"
COLLECTION_NAME = "climate_change_collection_langfuse"


def load_and_index_pdf(reindex: bool = False):
    """
    Carrega o PDF, divide em chunks e indexa no Qdrant local.

    Observabilidade (Langfuse):
      - 1 span raiz: load_and_index_pdf
      - spans filhos: check_collection, load_pdf, chunking, qdrant_prepare, qdrant_upsert

    Se reindex=False e a coleção existir, retorna o vectorstore existente.
    """

    langfuse = get_client()

    # Root span: tudo que acontecer aqui vira um único trace/spam raiz no Langfuse
    with langfuse.start_as_current_observation(
        name="RAG",
        as_type="span",
        input={"pdf_path": PDF_PATH, "collection": COLLECTION_NAME, "reindex": reindex},
    ):
        # Atributos úteis para filtrar/agrupuar no Langfuse (ajuste livremente)
        # Se você tiver user_id/session_id no seu app, coloque aqui também.
        with propagate_attributes(
            tags=["ingestion", "pdf", "qdrant"],
            metadata={
                "pdf_path": PDF_PATH,
                "collection_name": COLLECTION_NAME,
                "chunk_size": "1000",
                "chunk_overlap": "200",
                "qdrant_host": "localhost",
                "qdrant_port": "6333",
            },
        ):


            embeddings = OpenAIEmbeddings()

            # Inicializa cliente Qdrant local
            client = QdrantClient(host="localhost", port=6333)

            # --- Span 1: checar coleção ---
            with langfuse.start_as_current_observation(name="check_collection", as_type="span"):
                collections = client.get_collections().collections
                collection_exists = any(c.name == COLLECTION_NAME for c in collections)
                langfuse.update_current_span(
                    output={"collection_exists": collection_exists, "reindex": reindex}
                )

            if collection_exists and not reindex:
                print(f"--- Carregando coleção existente: {COLLECTION_NAME} ---")
                vectorstore = QdrantVectorStore(
                    client=client,
                    collection_name=COLLECTION_NAME,
                    embedding=embeddings,
                )
                langfuse.update_current_trace(
                    output={"status": "loaded_existing_collection", "collection": COLLECTION_NAME}
                )
                # Em scripts/CLI, flush evita perder eventos
                langfuse.flush()
                return vectorstore

            print(f"--- Indexando documento: {PDF_PATH} ---")

            # --- Span 2: carregar PDF ---
            with langfuse.start_as_current_observation(name="load_pdf", as_type="span"):
                if not os.path.exists(PDF_PATH):
                    # Langfuse marca erro automaticamente se a exceção subir
                    raise FileNotFoundError(f"PDF não encontrado: {PDF_PATH}")

                loader = PyPDFLoader(PDF_PATH)
                docs = loader.load()
                langfuse.update_current_span(output={"documents_loaded": len(docs)})

            # --- Span 3: chunking ---
            with langfuse.start_as_current_observation(name="chunking", as_type="span"):
                text_splitter = RecursiveCharacterTextSplitter(
                    chunk_size=1000,
                    chunk_overlap=200
                )
                splits = text_splitter.split_documents(docs)
                print(f"Criados {len(splits)} chunks.")
                langfuse.update_current_span(output={"chunks": len(splits)})

            # --- Span 4: preparar Qdrant (coleção) ---
            with langfuse.start_as_current_observation(name="qdrant_prepare", as_type="span"):
                # Recria coleção se forçado
                if reindex and collection_exists:
                    client.delete_collection(COLLECTION_NAME)
                    langfuse.update_current_span(metadata={"deleted_collection": True})

                if not client.collection_exists(COLLECTION_NAME):
                    client.create_collection(
                        collection_name=COLLECTION_NAME,
                        vectors_config=VectorParams(size=1536, distance=Distance.COSINE),
                    )
                    langfuse.update_current_span(metadata={"created_collection": True})

                vectorstore = QdrantVectorStore(
                    client=client,
                    collection_name=COLLECTION_NAME,
                    embedding=embeddings,
                )

            # --- Span 5: upsert (embeddings + add_documents) ---
            with langfuse.start_as_current_observation(name="qdrant_upsert", as_type="span"):
                # Este passo costuma ser o mais caro (embeddings + upsert)
                vectorstore.add_documents(splits)
                langfuse.update_current_span(output={"upserted_chunks": len(splits)})

            print("Indexação concluída!")

            langfuse.update_current_trace(
                output={
                    "status": "indexed",
                    "collection": COLLECTION_NAME,
                    "chunks": len(splits),
                }
            )
            # Em scripts/CLI, flush evita perder eventos
            langfuse.flush()
            return vectorstore