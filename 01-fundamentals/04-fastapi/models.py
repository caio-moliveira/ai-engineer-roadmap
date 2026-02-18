from pydantic import BaseModel

class GenerateRequest(BaseModel):
    capital: str 