# 📐 Modelagem de Dados com Pydantic: A Linguagem Franca da IA

> **Mantra:** "Garbage In, Garbage Out. Mas em IA, Garbage In = Alucinação."
> **Docs Oficiais:** [Pydantic](https://docs.pydantic.dev/) | [Instructor](https://github.com/jxnl/instructor)

Em Engenharia de IA, Pydantic não é apenas uma biblioteca de validação. É o **protocolo de comunicação** entre seu sistema determinístico (Python) e o modelo probabilístico (LLM).

---

## 1. Por que Pydantic é vital para IA?
LLMs são geradores de texto. O `GPT-4` não "sabe" o que é um JSON, ele apenas prediz que depois de `{ "name": "` vem um nome.
Se você pedir JSON puro em texto, ele pode retornar:
- JSON inválido (vírgula faltando).
- Tipos errados (string em vez de int).
- Campos alucinados que você não pediu.

**Pydantic resolve isso:**
1.  **Define o Schema:** Diz ao LLM exatamente quais campos existem e seus tipos.
2.  **Valida:** Se o LLM errar o tipo, o Pydantic lança erro.
3.  **Corrige (Retry):** Frameworks avançados usam o erro do Pydantic para pedir ao LLM corrigir a resposta automaticamente.

---

## 2. Structured Outputs (O Conceito Chave)
Ao invés de processar texto solto ("O cliente João comprou uma TV"), forçamos o LLM a "preencher" uma classe Pydantic.

### Exemplo Real: Extração de Dados de Notas Fiscais (Invoice Parsing)
Imagine receber um PDF bagunçado de uma nota fiscal.

```python
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date

class InvoiceItem(BaseModel):
    description: str
    quantity: int
    unit_price: float
    total_price: float

class Invoice(BaseModel):
    invoice_number: str = Field(..., description="O número oficial da nota, geralmente no topo.")
    issue_date: date = Field(..., description="Data de emissão da nota.")
    vendor_name: str
    items: List[InvoiceItem]
    tax_amount: Optional[float] = 0.0
    final_total: float

# O LLM agora "vê" essa estrutura e preenche os campos.
```

---

## 3. Na Prática: OpenAI Structured Outputs
A OpenAI agora suporta Pydantic nativamente. Isso garante 100% de aderência ao schema (json_schema_strict).

```python
import openai

client = openai.Client()

completion = client.beta.chat.completions.parse(
    model="gpt-4o-2024-08-06",
    messages=[
        {"role": "system", "content": "Extract the invoice data."},
        {"role": "user", "content": "Nota fiscal 001, emitida hoje para a TechCorp. 2 mouses a $50 cada."}
    ],
    response_format=Invoice, # Passamos a CLASSE Pydantic, não um dict
)

invoice_data = completion.choices[0].message.parsed
# invoice_data é uma INSTÂNCIA da classe Invoice real!
print(invoice_data.items[0].unit_price) # 50.0 (Float real, não string)
print(invoice_data.final_total) # 100.0
```

---

## 4. Validação como Regra de Negócio
O Pydantic permite regras lógicas. Se o LLM alucinar um preço total que não bate com a soma dos itens, podemos pegar isso **antes** de salvar no banco.

```python
from pydantic import model_validator

class Invoice(BaseModel):
    ...
    @model_validator(mode='after')
    def check_math(self):
        calculated = sum(item.total_price for item in self.items)
        if abs(self.final_total - calculated) > 0.01:
            raise ValueError(f"Total não bate! Soma: {calculated}, Nota: {self.final_total}")
        return self
```
*Se o LLM errar a matemática, o Pydantic explode um erro, e podemos usar esse erro para pedir ao LLM corrigir (Pattern de Self-correction).*

---

## 5. Instructor: O Canivete Suíço
Para modelos que não suportam Structured Outputs nativo (ou Open Source via Ollama/vLLM), usamos a biblioteca `Instructor`.

```bash
uv pip install instructor
```

O Instructor faz "monkey patch" no cliente da OpenAI para adicionar `.response_model` em qualquer LLM.

---

## ⏭️ Próximo Passo
Agora que temos dados limpos e estruturados, precisamos guardá-los de forma eficiente para busca semântica.
Vá para **[Módulo 05: Bancos de Dados (SQL + Vetorial)](../05-databases)**.
