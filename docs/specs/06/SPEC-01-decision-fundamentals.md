# SPEC-01: módulo 01, fundamentos

Status: concluída

## Objetivo
Mostrar o endpoint, o SDK, a mesma pergunta num LLM, o Laya local e a matriz de decisão.

## Cobre do PRD
Seção 7, Módulo 01.

## Interfaces
Scripts `01_http_direct.py`, `02_sdk_first_call.py`, `03_llm_same_question.py`, `04_laya_local.py` e `05_decision_matrix.py`.

## Critérios de aceite
- Os cinco scripts rodam em replay.
- `01` e `02` aceitam o alvo `laya` por argumento.
- `05` não chama modelo nenhum.

## Fora
Comparação extensa de modelos open-weight (fica só a tabela no README do bloco).
