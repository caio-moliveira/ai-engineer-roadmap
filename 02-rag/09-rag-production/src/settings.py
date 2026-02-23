from typing import Optional
from pydantic_settings import BaseSettings
import os
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL_ROUTER: str = "gpt-4o-mini"
    OPENAI_MODEL_ANSWER: str = "gpt-4.1"
    OPENAI_MODEL_RELEVANCE: Optional[str] = None
    OPENAI_EMBEDDING_MODEL: str = "text-embedding-3-large"
    
    QDRANT_HOST: str = "localhost"
    QDRANT_PORT: int = 6333
    QDRANT_COLLECTION_PRODUTOS: str = "produtos"
    QDRANT_COLLECTION_SUPORTE: str = "suporte"
    QDRANT_COLLECTION_ATENDIMENTO: str = "atendimento_especializado"
    
    LANGFUSE_PUBLIC_KEY: Optional[str] = None
    LANGFUSE_SECRET_KEY: Optional[str] = None
    LANGFUSE_BASE_URL: str = "https://cloud.langfuse.com"
    
    TOP_K: int = 5
    SCORE_THRESHOLD: float = 0.7
    FALLBACK_ORDER: str = "suporte,produtos,atendimento_especializado"

    @property
    def get_relevance_model(self) -> str:
        return self.OPENAI_MODEL_RELEVANCE or self.OPENAI_MODEL_ROUTER

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
