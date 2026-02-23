import time
from typing import List, Dict, Any, Optional
from qdrant_client import QdrantClient
from qdrant_client.http import models as rest
from langchain_openai import OpenAIEmbeddings
from src.settings import settings
from src.models import Chunk

def create_qdrant_client() -> QdrantClient:
    return QdrantClient(
        host=settings.QDRANT_HOST,
        port=settings.QDRANT_PORT
    )

def get_embeddings() -> OpenAIEmbeddings:
    return OpenAIEmbeddings(
        openai_api_key=settings.OPENAI_API_KEY,
        model=settings.OPENAI_EMBEDDING_MODEL
    )

def embed_text(text: str) -> List[float]:
    """Retorna embedding e latência em ms."""
    emb = get_embeddings()
    vector = emb.embed_query(text)
    return vector

def search_collection(collection_name: str, query_vector: List[float], top_k: int, metadata_filters: Optional[Dict[str, Any]] = None):
    client = create_qdrant_client()
    
    qdrant_filter = None
    if metadata_filters:
        must_conditions = []
        for key, value in metadata_filters.items():
            if isinstance(value, (str, int, float, bool)):
                must_conditions.append(rest.FieldCondition(key=key, match=rest.MatchValue(value=value)))
        if must_conditions:
            qdrant_filter = rest.Filter(must=must_conditions)

    results = client.query_points(
        collection_name=collection_name,
        query=query_vector,
        limit=top_k,
        query_filter=qdrant_filter
    ).points
    return results

def normalize_results(collection_name: str, query: str, qdrant_results) -> Dict[str, Any]:
    """
    Contract: {"collection":..., "query":..., "results":[{"text":..., "score":..., "metadata":...}]}
    """
    normalized_list = []
    for point in qdrant_results:
        payload = point.payload or {}
        text = payload.get("text", payload.get("page_content", "")) # standard fields for langchain
        
        if not text and payload:
            text = str(payload)

        chunk = Chunk(
            text=text,
            score=point.score,
            metadata={k: v for k, v in payload.items() if k not in ["text", "page_content"]}
        )
        normalized_list.append(chunk.model_dump())

    return {
        "collection": collection_name,
        "query": query,
        "results": normalized_list
    }
