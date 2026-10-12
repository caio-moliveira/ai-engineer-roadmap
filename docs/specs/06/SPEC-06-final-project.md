# SPEC-06: projeto final, agente híbrido

Status: concluída

## Objetivo
Um agente LangGraph com decisões em modelo de decisão e geração em LLM, medido ponta a ponta.

## Cobre do PRD
Seção 7, Módulo 06.

## Interfaces
- `config.yaml`: provider por node (`guardrail`, `triagem`, `verificacao`), modelo de geração e limiares.
- `graph.py: build_graph(config)`: guardrail, triagem, consulta, geração e verificação.
- `main.py`: `--lote`, `--comparar`, `--limite` e pergunta avulsa. Relatório em `saida/relatorio.md`.

## Critérios de aceite
- `python main.py --lote --comparar` roda em replay e imprime custo, latência p95, acurácia e concordância por provider.
- Trocar o provider de um node é editar uma linha do `config.yaml` (ou definir `AGENTE_PROVIDER`).

## Fora
Interface web (o workshop-jev tem uma) e banco Postgres (as tools leem resultados gravados).
