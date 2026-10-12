# SPEC-02: módulo 02, Choice

Status: concluída

## Objetivo
Substituir decisões de "qual" por um Choice e medir.

## Cobre do PRD
Seção 7, Módulo 02; RF-09 (`ModelRouterMiddleware`).

## Interfaces
Scripts `01_classify_tickets.py`, `02_tool_selection.py`, `03_model_routing.py`, `04_langchain_classifier.py` e `05_hierarchical.py`.

## Critérios de aceite
- Cada script imprime acurácia, latência e custo por provider.
- `02` compara o Choice com function calling (`bind_tools`).
- `04` roda `create_agent` com `ModelRouterMiddleware` em replay.

## Fora
Trocar o agente do Bloco 3 em si: é o exercício do módulo.
