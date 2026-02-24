from typing import Optional, Dict, Any, List, Literal
from pydantic import BaseModel, Field

import uuid

class AskRequest(BaseModel):
    question: str = Field(..., min_length=3)
    session_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    top_k: int = 3
    collection_name: str
    metadata_filters: Optional[Dict[str, Any]] = None

class DocumentMetadataExtraction(BaseModel):
    classificacao: str = Field(description="Classificação do documento em no máximo 3 palavras.")
    descricao: str = Field(description="Descrição resumida do documento em no máximo 2 frases.")

class Chunk(BaseModel):
    text: str
    score: float
    metadata: Dict[str, Any]

class AskResponse(BaseModel):
    answer: str
    collection_name: str
