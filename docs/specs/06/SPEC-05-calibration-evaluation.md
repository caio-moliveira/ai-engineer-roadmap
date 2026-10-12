# SPEC-05: módulo 05, calibração e avaliação

Status: concluída

## Objetivo
Transformar probabilidade em decisão de engenharia e medir de forma justa.

## Cobre do PRD
Seção 7, Módulo 05; RF-11.

## Interfaces
Scripts `01_golden_set.py`, `02_calibration.py`, `03_threshold_curve.py`, `04_fair_comparison.py` e `05_replay_record.py`.

## Critérios de aceite
- `02` e `03` salvam gráficos em `saida/`.
- `03` escolhe o limiar numa metade do golden set e relata na outra.
- `04` exporta CSV e, em modo live, pede `--confirmar` acima de US$ 1 estimado.
- `05` reaproveita o que já foi gravado e só regrava com `--forcar`.

## Fora
Calibração isotônica (o módulo mostra só ajuste de temperatura).
