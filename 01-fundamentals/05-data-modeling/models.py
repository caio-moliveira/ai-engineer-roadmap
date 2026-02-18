from pydantic import BaseModel

class GenerateRequest(BaseModel):
    capital: str 

class CapitalData(BaseModel):
    population: int
    country: str
    currency: str
    language: str
    curiosity: str
