# SPEC-07: módulo 07 (bônus)

Status: concluída

## Objetivo
Mostrar o que há por baixo de um modelo de decisão e um caminho open-weight sob medida.

## Cobre do PRD
Seção 7, Módulo 07; RF-10.

## Interfaces
Scripts `01_scoring_head.py`, `02_finetune_laya.py` e `03_serve_systemone.py`.

## Critérios de aceite
- `01` e `02` rodam em CPU com `--rapido` (incluídos no smoke test com `RUN_HEAVY=1`).
- `03` serve `/v1/systemone` e é chamado pelo SDK do Jev sem mudança de código.

## Fora
Treino distribuído e exportação ONNX.
