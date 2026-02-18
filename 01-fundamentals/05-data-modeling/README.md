# Pydantic para Workflows com LLM (v2) 

## Objetivo
Ao final, você vai conseguir:
1. Definir **schemas** como “contrato” para saída de LLM.
2. Validar, normalizar e serializar dados com **Pydantic v2**.
3. Implementar **retries com feedback de erro estruturado** (padrão ouro em produção).
4. Usar tipos avançados (Enum, datetime, UUID, URLs, Decimal, IP) e **unions discriminadas** para respostas “uma de várias formas”.
5. Configurar `.env` via **pydantic-settings**.

---

## 0) Setup recomendado

```bash
pip install -U pydantic pydantic-settings
# se for usar validação de e-mail:
pip install "pydantic[email]"
```

---

## 1) Por que Pydantic é essencial com LLM?

LLMs geram texto “fluente”, mas **não garantem estabilidade**: campo faltando, nome diferente, tipo errado, JSON inválido… Schema vira a “camada de confiabilidade” do pipeline.

**Padrão mental**:
> LLM escreve “rascunho” → Pydantic transforma em “dado de produção”.

---

## 2) Field constraints: required/optional/defaults/regex/ranges

Veja exemplo em `01_basic_fields.py`.

### Conceitos Chave:
* **Obrigatório**: sem valor padrão (ou usando `Field(...)`)
* **Opcional**: `T | None` / `Optional[T]`
* **Default**: `field: T = valor`
* **Default factory**: `default_factory=...` (cria valor em runtime, ex: timestamp, list nova etc.)
* **Restrições**: `ge, gt, le, lt`, `min_length`, `max_length`, `pattern`/`regex`

**Notas importantes para LLM:**
* Campos opcionais são essenciais quando o texto não traz evidência (“não citado” vira `None`).
* `pattern/regex` e ranges (`ge/le`) reduzem alucinações “fora do domínio” (ex: confiança > 1).

---

## 3) Pydantic v2: validação customizada

Veja exemplo em `02_validators.py`.

### Tipos de Validadores:
1. **`@field_validator`**: Normalizar strings, limpar dados.
2. **`@model_validator`**: Validação cruzada entre campos (ex: se prioridade alta, título deve conter etiqueta).

---

## 4) model_validate(), model_dump(), model_dump_json()

Veja exemplo em `03_serialization.py`.

No v2, os métodos “clarearam” os nomes:
* `Model.model_validate(obj)` → valida e converte
* `Model.model_validate_json(str)` → valida string JSON
* `model_dump()` → converte para dict python
* `model_dump_json()` → serializa para string JSON

---

## 5) Tipos ricos: Enums, datetime, UUID, IPs, URLs, Decimals

Veja exemplo em `04_types.py`.

Esses tipos são **muito úteis para “domar” categorias e identificadores** em saída de LLM.
* `Decimal`: Evita bugs de float em dinheiro.
* `HttpUrl`: Garante URLs válidas.
* `Enum`: Restringe opções de texto (ex: "active", "inactive").

---

## 6) Discriminated unions (Union, Literal, Annotated)

Veja exemplo em `05_unions.py`.

LLM muitas vezes retorna **“um de vários formatos”** (ex: action pode ser “create_ticket” ou “ask_followup”).
Use `Literal` como discriminador para o Pydantic saber qual classe instanciar.

---

## 7) BaseSettings (pydantic_settings) para .env

Veja exemplo em `06_settings.py`.

Para aplicações com LLM, você quase sempre tem senhas e configurações.
Use `BaseSettings` para carregar de variáveis de ambiente (`.env`).

---

## 8) Error handling: mensagens estruturadas (ValidationError)

Veja exemplo em `07_error_handling.py`.

A sacada que mais eleva o nível em LLM pipelines é: **usar os erros estruturados do Pydantic para re-prompt**.
Você transforma `e.errors()` em feedback objetivo pro modelo corrigir o JSON.

---

## 9) Pipeline completo: Extração estruturada com retry guiado por validação

Veja exemplo em `08_pipeline.py`.

O fluxo padrão ouro:
1. LLM gera JSON.
2. Pydantic valida.
3. Se falhar: pega erro, adiciona ao prompt ("Corrija estes erros...") e tenta de novo.
4. Sucesso: Retorna objeto tipado.

---
