"""Módulo 05 · Script 03: curva de automação por limiar.

Pergunta-chave: com limiar 0,85, quanto você automatiza e com que precisão?

Para cada limiar: as decisões com confiança acima dele são automatizadas; as demais vão
para um humano. A curva mostra a troca entre cobertura (% automatizado) e acurácia no
subconjunto automatizado.

O limiar é ESCOLHIDO numa metade do golden set e RELATADO na outra. Escolher e relatar no
mesmo dado é otimismo garantido.

Rode: python 05-calibration-evaluation/03_threshold_curve.py
Saída: 05-calibration-evaluation/saida/automacao_fila.png
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from common import golden, metrics
from common.evaluation import automation_inputs, print_table, run_targets
from common.providers import compare_targets
from common.specs import FILA

ACURACIA_MINIMA = 0.95  # requisito do negócio: errar no máximo 1 em 20 do que é automatizado
LIMIARES = [0.0, 0.5, 0.6, 0.7, 0.8, 0.85, 0.9, 0.95, 0.98, 0.99]

tickets = golden.load("tickets")
runs_by_target = run_targets(compare_targets(), tickets, [FILA])

fig, ax = plt.subplots(figsize=(7, 5))
curva_rows, escolha_rows = [], []
for target, runs in runs_by_target.items():
    confs, correct = automation_inputs(FILA, runs)
    points = metrics.automation_curve(confs, correct, LIMIARES)
    for p in points:
        curva_rows.append({"provider": target, "limiar": p.threshold, "automatizado": p.coverage,
                           "acurácia automatizada": p.accuracy, "para humano": p.total - p.automated})
    ax.plot([p.coverage for p in points], [p.accuracy or 0 for p in points], marker="o", label=target)

    ajuste, teste = runs[0::2], runs[1::2]
    escolhido = metrics.best_threshold(metrics.automation_curve(*automation_inputs(FILA, ajuste), LIMIARES), ACURACIA_MINIMA)
    if escolhido is None:
        escolha_rows.append({"provider": target, "limiar escolhido": None, "automatizado (teste)": None,
                             "acurácia (teste)": None, "nota": f"nenhum limiar chega a {ACURACIA_MINIMA:.0%}"})
        continue
    [no_teste] = metrics.automation_curve(*automation_inputs(FILA, teste), [escolhido.threshold])
    escolha_rows.append({"provider": target, "limiar escolhido": escolhido.threshold,
                         "automatizado (teste)": no_teste.coverage, "acurácia (teste)": no_teste.accuracy,
                         "nota": "ok" if (no_teste.accuracy or 0) >= ACURACIA_MINIMA else "não segurou no teste"})

print_table(curva_rows, "Curva de automação: Choice 'fila' (golden set inteiro)")
print_table(escolha_rows, f"Limiar escolhido na metade de ajuste para acurácia >= {ACURACIA_MINIMA:.0%}, medido na metade de teste")

ax.axhline(ACURACIA_MINIMA, linestyle="--", color="gray", label=f"requisito {ACURACIA_MINIMA:.0%}")
ax.set_xlabel("% automatizado (confiança >= limiar)")
ax.set_ylabel("acurácia no automatizado")
ax.set_title("Automação x acurácia por limiar")
ax.legend(fontsize=8)
fig.tight_layout()
saida = Path(__file__).resolve().parent / "saida"
saida.mkdir(exist_ok=True)
fig.savefig(saida / "automacao_fila.png", dpi=120)
print(f"\nCurva salva em {saida / 'automacao_fila.png'}")
print(
    "\nUm provider mal calibrado faz a curva mentir: confiança alta não separa acerto de erro,"
    "\ne subir o limiar só reduz a cobertura sem ganhar acurácia. É por isso que calibração vem"
    "\nantes de limiar (script 02)."
)
