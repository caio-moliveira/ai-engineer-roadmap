from typing import Optional, Dict, Any, List, Literal
from pydantic import BaseModel, Field

import uuid

class AskRequest(BaseModel):
    question: str = Field(..., min_length=3)
    session_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    top_k: int = 3
    collection_hint: Optional[Literal["produtos", "suporte", "atendimento_especializado"]] = None
    metadata_filters: Optional[Dict[str, Any]] = None

class Chunk(BaseModel):
    text: str
    score: float
    metadata: Dict[str, Any]

class AskResponse(BaseModel):
    answer: str
    route: Literal["produtos", "suporte", "atendimento_especializado", "unknown"]
    used_collections: List[Literal["produtos", "suporte", "atendimento_especializado"]]
    confidence: float
    evidence: List[Chunk]
    warnings: List[str] = []
