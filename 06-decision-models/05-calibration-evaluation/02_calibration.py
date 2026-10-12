"""Módulo 05 · Script 02: calibração. A confiança quer dizer o que diz?

Calibrado é: entre cem respostas com 74% de confiança, cerca de 74 estão certas.
- ECE (Expected Calibration Error): distância média entre confiança e acerto, por faixa. 0 é perfeito.
- Brier: erro quadrático da probabilidade. Mistura acerto e calibração. Menor é melhor.
- Diagrama de confiabilidade: confiança média x acurácia por faixa. Calibrado = diagonal.

Para o LLM, a "confiança" é autorrelatada (ele escreveu o número). Para Jev e Laya, vem da
distribuição. O Laya multilíngue sai sem calibração de fábrica; o fim do script mostra o
remédio clássico, ajuste de temperatura, escolhido numa metade e medido na outra.

Rode: python 05-calibration-evaluation/02_calibration.py
Saída: 05-calibration-evaluation/saida/calibracao_fila.png
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from common import golden, metrics
from common.evaluation import automation_inputs, print_table, run_targets, summarize
from common.providers import compare_targets
from common.specs import FILA, SPAM_DIRETO, URGENCIA

SAIDA = Path(__file__).resolve().parent / "saida"
SAIDA.mkdir(exist_ok=True)

TAREFAS = [("tickets", FILA), ("tickets", URGENCIA), ("spam", SPAM_DIRETO)]

resultados = {}
rows = []
for dataset, spec in TAREFAS:
    items = golden.load(dataset)
    for target, runs in run_targets(compare_targets(), items, [spec]).items():
        resultados[(spec.name, target)] = runs
        s = summarize(spec, runs)
        confs, correct = automation_inputs(spec, runs)
        rows.append({
            "pergunta": f"{spec.name} ({spec.type})",
            "provider": s["provider"],
            "acurácia": s["acurácia"],
            "confiança média": sum(confs) / len(confs),
            "excesso de confiança": sum(confs) / len(confs) - s["acurácia"],
            "ece": s["ece"],
            "brier": s["brier"],
        })
print_table(rows, "Calibração por pergunta e provider")
print("'excesso de confiança' > 0: o provider diz estar mais seguro do que acerta.")

# --- Diagrama de confiabilidade para a fila -------------------------------------------------
fig, ax = plt.subplots(figsize=(6, 6))
ax.plot([0, 1], [0, 1], linestyle="--", color="gray", label="calibração perfeita")
bins_rows = []
for (name, target), runs in resultados.items():
    if name != "fila":
        continue
    confs, correct = automation_inputs(FILA, runs)
    bins = [b for b in metrics.reliability_bins(confs, correct, n_bins=10) if b.count]
    ax.plot([b.mean_confidence for b in bins], [b.accuracy for b in bins], marker="o", label=target)
    for b in bins:
        bins_rows.append({"provider": target, "faixa": f"{b.lower:.1f}–{b.upper:.1f}", "n": b.count,
                          "confiança média": b.mean_confidence, "acurácia": b.accuracy})
ax.set_xlabel("confiança média da faixa")
ax.set_ylabel("acurácia da faixa")
ax.set_title("Diagrama de confiabilidade: Choice 'fila'")
ax.legend(loc="upper left", fontsize=8)
fig.tight_layout()
fig.savefig(SAIDA / "calibracao_fila.png", dpi=120)
print_table(bins_rows, "Faixas de confiança da pergunta 'fila'")
print(f"\nDiagrama salvo em {SAIDA / 'calibracao_fila.png'}")

# --- Remédio: ajuste de temperatura (escolhe T numa metade, mede na outra) -------------------


def with_temperature(dist: dict[str, float], t: float) -> dict[str, float]:
    logits = {k: math.log(max(p, 1e-9)) / t for k, p in dist.items()}
    m = max(logits.values())
    exp = {k: math.exp(v - m) for k, v in logits.items()}
    z = sum(exp.values())
    return {k: v / z for k, v in exp.items()}


def nll(runs, t: float) -> float:
    return -sum(math.log(max(with_temperature(r.result.answers["fila"].probabilities, t)[r.item.labels["fila"]], 1e-9)) for r in runs)


def ece_with(runs, t: float) -> float:
    confs, correct = [], []
    for r in runs:
        d = with_temperature(r.result.answers["fila"].probabilities, t)
        pred = max(d, key=d.get)
        confs.append(d[pred])
        correct.append(pred == r.item.labels["fila"])
    return metrics.ece(confs, correct)


temp_rows = []
for (name, target), runs in resultados.items():
    if name != "fila" or not all(r.result.answers.get("fila") and r.result.answers["fila"].probabilities for r in runs):
        continue  # LLM sem distribuição: não há o que reescalar
    ajuste, teste = runs[0::2], runs[1::2]
    t_best = min((x / 20 for x in range(5, 101)), key=lambda t: nll(ajuste, t))
    temp_rows.append({"provider": target, "T escolhido (metade de ajuste)": t_best,
                      "ECE antes (metade de teste)": ece_with(teste, 1.0), "ECE depois (metade de teste)": ece_with(teste, t_best)})
if temp_rows:
    print_table(temp_rows, "Ajuste de temperatura na pergunta 'fila'")
    print("T > 1 achata a distribuição (o modelo estava confiante demais); T < 1 a afia."
          "\nCom 30 exemplos de ajuste, o T é instável: em produção, ajuste com centenas, por tipo de pergunta.")
