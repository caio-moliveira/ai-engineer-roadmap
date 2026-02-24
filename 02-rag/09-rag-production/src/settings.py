from typing import Optional
from pydantic_settings import BaseSettings
import os
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    
    QDRANT_HOST: str = "localhost"
    QDRANT_PORT: int = 6333
    
    LANGFUSE_PUBLIC_KEY: Optional[str] = None
    LANGFUSE_SECRET_KEY: Optional[str] = None
    LANGFUSE_BASE_URL: str = "https://cloud.langfuse.com"
    
    OPENAI_API_KEY: Optional[str] = None
    

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
