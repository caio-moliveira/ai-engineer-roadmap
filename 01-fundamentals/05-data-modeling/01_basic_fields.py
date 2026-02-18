from datetime import datetime, timezone
from typing import Optional
from pydantic import BaseModel, Field, EmailStr

# --- 1. Campo obrigatório vs opcional vs default ---

class UserProfile(BaseModel):
    # Campo obrigatório: usa Field(...) ou apenas a anotação de tipo sem default
    name: str = Field(..., min_length=1, description="Nome completo do usuário")

    # Tipo especializado (valida formato de e-mail automaticamente)
    email: EmailStr

    # Opcional + constraints numéricas
    # Default é None, então se o LLM não enviar, fica None
    age: Optional[int] = Field(default=None, ge=0, le=120, description="Idade em anos")

    # Default com valor fixo
    bio: str = Field(default="", max_length=500, description="Biografia curta")

    # Regex/Pattern para padronizar valores (ótimo para categorias fixas simples)
    role: str = Field(default="user", pattern=r"^(user|admin|moderator)$")

# --- 2. default_factory (Valores dinâmicos) ---

class Trace(BaseModel):
    request_id: str = Field(..., description="ID único da requisição")
    
    # default_factory executa a função a cada nova instância
    # Útil para datas, UUIDs, listas mutáveis, etc.
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

# --- Exemplo de Uso ---

if __name__ == "__main__":
    print("--- Exemplo 1: Dados Completos ---")
    data_valid = {
        "name": "Alice",
        "email": "caio",
        "age": 300,
        "role": "admin",
        "bio": "Engenheira de IA"
    }
    user = UserProfile.model_validate(data_valid)
    print(user)

    print("\n--- Exemplo 2: Dados Parciais (Defaults) ---")
    data_partial = {
        "name": "Bob",
        "email": "caio@gmail.com"
    }
    user_partial = UserProfile.model_validate(data_partial)
    print(user_partial)

    print("\n--- Exemplo 3: Default Factory ---")
    trace = Trace(request_id="12345")
    print(trace)
