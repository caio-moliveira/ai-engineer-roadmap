# SPEC-03: módulo 03, Noul

Status: concluída

## Objetivo
Decompor perguntas amplas em Nouls verificáveis, na entrada e na saída do LLM.

## Cobre do PRD
Seção 7, Módulo 03; RF-09 (`AutoModeMiddleware`).

## Interfaces
Scripts `01_spam_decomposed.py`, `02_multilabel.py`, `03_guardrail_input.py`, `04_verify_output.py` e `05_langchain_middleware.py`.

## Critérios de aceite
- `03` mostra recall e taxa de falso positivo por limiar.
- `05` roda o `AutoModeMiddleware` num `create_agent` em replay e compara com `golden_tool_calls.json`.

## Fora
Aprovação humana (fica com o Bloco 3).
