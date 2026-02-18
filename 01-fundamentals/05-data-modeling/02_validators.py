from pydantic import BaseModel, Field, field_validator, model_validator

class Ticket(BaseModel):
    title: str = Field(..., min_length=3)
    priority: int = Field(..., ge=1, le=5)
    tags: list[str] = Field(default_factory=list)

    # --- 1. @field_validator: Validação de um campo específico ---
    @field_validator("title")
    @classmethod
    def normalize_title(cls, v: str) -> str:
        """
        Normaliza o título: remove espaços e garante que não seja vazio.
        Comum converter "N/A" ou "unknown" para valores padrão se necessário.
        """
        v = v.strip()
        if not v:
            raise ValueError("title não pode ser vazio")
        # Exemplo de limpeza comum em LLM output
        if v.lower() in ["n/a", "unknown", "none"]:
            raise ValueError("Title inválido gerado pelo LLM")
        return v.title() # Capitalize

    @field_validator("tags")
    @classmethod
    def unique_tags(cls, v: list[str]) -> list[str]:
        """Remove duplicatas preservando ordem"""
        return list(dict.fromkeys(v))

    # --- 2. @model_validator: Validação cruzada (vários campos) ---
    @model_validator(mode="after")
    def check_priority_rule(self):
        """
        Regra de negócio: Se a prioridade for alta (>=4), 
        o título deve conter marcadores de urgência.
        """
        if self.priority >= 4:
            if not any(marker in self.title.upper() for marker in ["[URGENTE]", "CRÍTICO"]):
                # Podemos injetar automaticamente ou levantar erro.
                # Aqui vamos levantar erro para forçar o LLM a corrigir.
                raise ValueError("Para prioridade >=4, o título deve conter '[URGENTE]' ou 'CRÍTICO'")
        return self

# --- Exemplo de Uso ---

if __name__ == "__main__":
    try:
        print("--- Teste 1: Normalização ---")
        t1 = Ticket(title="  bug no login  ", priority=3, tags=["bug", "bug", "frontend"])
        print(f"Título normalizado: '{t1.title}'")
        print(f"Tags únicas: {t1.tags}")

        print("\n--- Teste 2: Validação Cruzada (Erro) ---")
        # Isso vai falhar porque priority=5 exige [URGENTE] no título
        t2 = Ticket(title=" Erro simples", priority=5)
        print(t2)
    except ValueError as e:
        print(f"Erro capturado: {e}")

    print("\n--- Teste 3: Validação Cruzada (Sucesso) ---")
    t3 = Ticket(title="[URGENTE] Sistema fora do ar", priority=5)
    print(t3)
