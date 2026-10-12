"""Módulo 04 · Script 03: Score como judge barato de respostas do LLM.

Rubrica de qualidade em 4 níveis sobre (pergunta, dados, resposta). Comparamos:
- concordância de cada judge com o rótulo humano do golden set;
- concordância entre o judge de decisão (Jev/Laya) e o judge LLM, que é o que muita gente
  usa hoje em avaliação contínua.

Se o judge de decisão concorda com o judge LLM tanto quanto dois humanos concordariam,
ele pode rodar em 100% do tráfego pelo custo de uma amostra.

Rode: python 04-score-ranking/03_quality_judge.py
"""

import sys
from itertools import combinations
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from common import golden, metrics
from common.evaluation import prediction, print_table, run_targets, summarize
from common.providers import compare_targets
from common.specs import QUALIDADE

respostas = golden.load("verify")
print("Rubrica:")
for nivel, desc in enumerate(QUALIDADE.criteria):
    print(f"  {nivel}: {desc}")

runs_by_target = run_targets(compare_targets(), respostas, [QUALIDADE])
humano = [r.labels["qualidade"] for r in respostas]

rows = []
notas = {}
for target, runs in runs_by_target.items():
    s = summarize(QUALIDADE, runs)
    notas[target] = [prediction(QUALIDADE, r) for r in runs]
    rows.append({
        "judge": s["provider"],
        "acurácia vs humano": s["acurácia"],
        "kappa vs humano": metrics.cohen_kappa(humano, notas[target]),
        "erro ±1 nível": sum(abs((p if p is not None else 0) - h) <= 1 for p, h in zip(notas[target], humano)) / len(humano),
        "p95_ms": s["p95_ms"],
        "custo_1k_usd": s["custo_1k_usd"],
    })
print_table(rows, "Judge de qualidade contra o rótulo humano")

pares = [{"judge A": a, "judge B": b, "concordância": metrics.agreement(notas[a], notas[b]),
          "kappa": metrics.cohen_kappa(notas[a], notas[b])} for a, b in combinations(notas, 2)]
if pares:
    print_table(pares, "Concordância entre judges")

print(
    "\nKappa acima de ~0,6 costuma ser lido como concordância substancial. Antes de trocar o judge"
    "\nLLM pelo Score, meça isto no SEU golden set: uma rubrica mal escrita derruba os dois."
)
