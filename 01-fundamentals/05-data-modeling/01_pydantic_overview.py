from datetime import datetime, timezone
from decimal import Decimal
from enum import Enum
from ipaddress import IPv4Address
from typing import Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, EmailStr, HttpUrl, field_validator, model_validator

# --- 1. Definição de Tipos e Enums ---

class Role(str, Enum):
    """Enum simplifica validação de escolhas fixas"""
    USER = "user"
    ADMIN = "admin"
    MODERATOR = "moderator"

# --- 2. Modelo Unificado ---

class UserProfile(BaseModel):
    # Identificadores e Tipos Complexos
    id: UUID = Field(default_factory=uuid4, description="ID único gerado automaticamente")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    # Campos Básicos com Restrições
    name: str = Field(..., min_length=2, max_length=50, description="Nome completo")
    email: EmailStr
    
    # Opcionais e Defaults
    age: Optional[int] = Field(default=None, ge=0, le=120, description="Idade opcional")
    role: Role = Field(default=Role.USER)
    
    # Tipos Especializados
    website: Optional[HttpUrl] = None
    balance: Decimal = Field(default=Decimal(0), ge=0, decimal_places=2)
    last_ip: Optional[IPv4Address] = None
    
    # Tags para demonstrar list e factory
    tags: list[str] = Field(default_factory=list)

    # --- 3. Validadores Customizados (@field_validator) ---
    
    @field_validator("name")
    @classmethod
    def normalize_name(cls, v: str) -> str:
        """Limpa espaços e capitaliza o nome"""
        v = v.strip().title()
        if not v:
            raise ValueError("Nome não pode ser vazio")
        return v

    @field_validator("tags")
    @classmethod
    def unique_tags(cls, v: list[str]) -> list[str]:
        """Remove duplicatas das tags"""
        return list(dict.fromkeys(v))

    # --- 4. Validação Cruzada (@model_validator) ---
    
    @model_validator(mode="after")
    def check_admin_security(self):
        """Regra de negócio: Admins devem ter IP registrado"""
        if self.role == Role.ADMIN and not self.last_ip:
            raise ValueError("Administradores exigem registro de IP (last_ip)")
        return self

# --- 5. Execução e Testes ---

if __name__ == "__main__":
    print("\n=== Exemplo 1: Sucesso (Dados Completos) ===")
    data_valid = {
        "name": "  alice wonderland  ",  # Vai ser normalizado
        "email": "caio@gmail.com",
        "age": 30,
        "role": "admin",
        "website": "https://example.com/alice",
        "balance": "150.50", # String convertida para Decimal
        "last_ip": "192.168.1.10",
        "tags": ["ia", "python", "ia"] # Duplicata será removida
    }
    
    try:
        user = UserProfile.model_validate(data_valid)
        print("Objeto criado com sucesso:")
        print(user.model_dump_json(indent=2))
        
        print(f"\nTipos convertidos:")
        print(f"- Balance: {type(user.balance)} = {user.balance}")
        print(f"- Website: {type(user.website)} = {user.website}")
        print(f"- ID: {user.id}")
        
    except Exception as e:
        print(f"Erro inesperado: {e}")

    print("\n=== Exemplo 2: Erro de Validação (Regra de Negócio) ===")
    data_invalid = {
        "name": "Bob Hacker",
        "email": "caio@gmail.com",
        "role": "admin",
        "last_ip": "192.168.1.10"
        # Falta IP, o que deve gerar erro pela regra check_admin_security
    }
    
    try:
        UserProfile.model_validate(data_invalid)
    except Exception as e:
        print("Erro capturado corretamente:")
        print(e)
        
    print("\n=== Exemplo 3: Serialização (Dict e JSON) ===")
    # Usando o objeto do exemplo 1
    if 'user' in locals():
        # model_dump -> Dict
        user_dict = user.model_dump(exclude_none=True)
        print(f"Dict (sem Nones): {user_dict.keys()}")
