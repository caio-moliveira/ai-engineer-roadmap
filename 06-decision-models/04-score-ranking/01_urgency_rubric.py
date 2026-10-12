"""Módulo 04 · Script 01: Score de urgência em três níveis.

Um Score é uma rubrica ORDENADA: o nível 2 é mais que o 1, que é mais que o 0. O modelo de
decisão devolve a distribuição sobre os níveis e o valor esperado (`score`), um número
contínuo. É ele que ordena a fila: dois tickets "nível 2" deixam de empatar.

Rode: python 04-score-ranking/01_urgency_rubric.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from common import golden, metrics
from common.evaluation import print_table, run_targets, summarize
from common.providers import compare_targets
from common.specs import URGENCIA

tickets = golden.load("tickets")
print("Rubrica:")
for nivel, desc in enumerate(URGENCIA.criteria):
    print(f"  {nivel}: {desc}")

def valor_esperado(answers) -> float:
    """Jev e Laya devolvem o valor esperado; o LLM só devolve o nível inteiro."""
    a = answers.get("urgencia")
    if a is None:
        return 1.0  # sem resposta: meio da escala
    return a.expected if a.expected is not None else float(a.value)


runs_by_target = run_targets(compare_targets(), tickets, [URGENCIA])
rows = []
for runs in runs_by_target.values():
    s = summarize(URGENCIA, runs)
    truth = [r.item.labels["urgencia"] for r in runs]
    expected = [valor_esperado(r.result.answers) for r in runs]
    # Ordenação da fila: quanto dos 10 primeiros é realmente "resolver hoje"?
    fila = sorted(range(len(runs)), key=lambda i: -expected[i])
    top10 = [truth[i] for i in fila[:10]]
    rows.append({
        "provider": s["provider"],
        "acurácia (nível)": s["acurácia"],
        "erro médio (níveis)": sum(abs(e - t) for e, t in zip(expected, truth)) / len(truth),
        "nDCG@10 da fila": metrics.ndcg_at_k([truth[i] for i in fila], 10),
        "urgentes no top 10": f"{sum(t == 2 for t in top10)}/10",
        "empates no topo": len(fila[:10]) - len({round(expected[i], 4) for i in fila[:10]}),
        "brier": s["brier"],
    })
print_table(rows, "Urgência: acerto do nível e qualidade da fila ordenada")

print(f"\nNo golden set há {sum(t.labels['urgencia'] == 2 for t in tickets)} tickets de nível 2.")
print(
    "O LLM devolve um inteiro: dez tickets 'nível 2' empatam e a ordem entre eles é sorte."
    "\nO valor esperado do Score desempata com a própria incerteza do modelo."
    "\n\nAtenção com o Laya multilíngue: o model card registra viés de posição em Score (ele"
    "\nraramente escolhe o primeiro nível). Meça no seu dado antes de confiar."
)
