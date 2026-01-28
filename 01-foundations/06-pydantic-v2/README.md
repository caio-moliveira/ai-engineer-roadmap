# 🛡️ Módulo 6: Pydantic v2

> **Goal:** Transformar o caos do texto em ordem estruturada.  
> **Status:** A linguagem franca entre Python e LLMs.

## 1. Schema First Development
Em IA, você não escreve o prompt e torce para o JSON sair certo.
Você define o Schema Pydantic *primeiro*, e usa ele para gerar as instruções para o modelo.

## 2. Validação Rigorosa
Pydantic não é só para tipos. É para regras de negócio.

```python
from pydantic import BaseModel, Field, field_validator

class UserQuery(BaseModel):
    age: int = Field(gt=0, lt=120)
    
    @field_validator('age')
    @classmethod
    def check_legal_age(cls, v):
        if v < 18:
            raise ValueError("Serviço apenas para maiores")
        return v
```

## 3. Deserialização Segura
LLMs são notórios por errar vírgulas em JSON.
Pydantic v2 (escrito em Rust) é extremamente tolerante e rápido para parsear outputs, e lança erros descritivos que você pode (incrível!) mandar de volta para o LLM se corrigir ("Retry Parsing").

## 🧠 Mental Model: "O Tradutor Universal"
O LLM "pensa" em tokens (texto).
Seu sistema "pensa" em Objetos (Structs).
O Pydantic é a ponte segura entre esses dois mundos.

## ⏭️ Próximo Passo
Como pensamos sobre tudo isso junto?
Vá para **[Módulo 7: Mentalidade de Engenharia](../07-engineering-mindset)**.
