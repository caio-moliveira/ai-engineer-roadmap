from pydantic import BaseModel, Field

class GenerateRequest(BaseModel):
    capital: str = Field(..., min_length=2, max_length=50, description="Nome da capital")

class CapitalData(BaseModel):
    populacao: int
    pais: str = Field(..., min_length=2, max_length=50, description="Nome do país")
    moeda: str = Field(..., min_length=2, max_length=50, description="Moeda do país")
    lingua: str = Field(..., min_length=2, max_length=50, description="Lingua do país")
    curiosidade: str = Field(..., min_length=2, max_length=500, description="Curiosidade do país")
