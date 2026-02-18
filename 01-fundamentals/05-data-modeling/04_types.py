from datetime import datetime, timezone
from decimal import Decimal
from enum import Enum
from ipaddress import IPv4Address
from uuid import UUID, uuid4
from pydantic import BaseModel, HttpUrl, Field

# --- 1. Definindo um Enum (Melhor que string solta) ---
# Enums garantem que o LLM não retorne "Active", "ativado", "sim", etc.
class Status(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    PENDING = "pending"

class Resource(BaseModel):
    # UUID: Valida formato de ID único
    id: UUID = Field(default_factory=uuid4)
    
    # Enum: Só aceita valores definidos
    status: Status
    
    # HttpUrl: Garante que é uma URL válida (http/https)
    url: HttpUrl
    
    # Datetime: Pydantic parseia ISO formats string -> datetime object
    created_at: datetime
    
    # Decimal: Essencial para valores monetários (float tem erros de precisão)
    balance: Decimal
    
    # IPv4Address: Valida IPs
    ip: IPv4Address

# --- Exemplo de Uso ---

if __name__ == "__main__":
    print("--- Validando Tipos Complexos ---")
    
    # Simulando output de LLM
    data = {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "status": "active",
        "url": "https://api.example.com/v1/resource",
        "created_at": "2023-10-27T10:00:00Z",
        "balance": "150.50",
        "ip": "192.168.1.1"
    }

    resource = Resource.model_validate(data)
    
    print(f"ID (UUID): {resource.id}")
    print(f"Status (Enum): {resource.status}")
    print(f"URL (HttpUrl): {resource.url}")
    print(f"Balance (Decimal): {resource.balance} (tipo: {type(resource.balance)})")
    print(f"IP (IPv4): {resource.ip}")

