# SPEC-04: módulo 04, Score

Status: concluída

## Objetivo
Usar rubricas ordenadas para ordenar, priorizar e extrair features.

## Cobre do PRD
Seção 7, Módulo 04.

## Interfaces
Scripts `01_urgency_rubric.py`, `02_rerank_rag.py`, `03_quality_judge.py` e `04_text_to_features.py`.

## Critérios de aceite
- `02` mede recall@5 e nDCG@5 contra a ordem do retriever.
- `03` mede kappa contra o rótulo humano e entre judges.
- `04` compara CatBoost com e sem as features de decisão, em validação cruzada.

## Fora
Qdrant ao vivo no `02`: os candidatos estão congelados em `data/golden_rerank.json`.
