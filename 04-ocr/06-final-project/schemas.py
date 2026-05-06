from typing import Optional
from pydantic import BaseModel


class ReceiptOut(BaseModel):
    id: str
    description: Optional[str]
    amount: Optional[float]
    purchase_time: Optional[str]
    location: Optional[str]
    raw_text: Optional[str]
    created_at: str


class ReceiptPatch(BaseModel):
    description: Optional[str] = None
    amount: Optional[float] = None
    purchase_time: Optional[str] = None
    location: Optional[str] = None
