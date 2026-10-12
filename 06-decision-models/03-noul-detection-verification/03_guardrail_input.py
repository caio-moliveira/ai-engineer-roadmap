"""Módulo 03 · Script 03: guardrail de entrada com três Nouls.

Antes de o agente de vendas tocar no banco ou no LLM: a mensagem tenta manipular o
assistente? pede dado pessoal sensível? está fora do escopo? Cada pergunta é um Noul;
o código bloqueia se qualquer probabilidade passar do limiar.

O limiar troca uma taxa por outra: mais baixo pega mais ataques e bloqueia mais perguntas
legítimas (falso positivo). Medimos os dois no golden set de vendas (60 legítimas + 20 adversariais).

Rode: python 03-noul-detection-verification/03_guardrail_input.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from common import golden, metrics
from common.evaluation import print_table, run_targets, summarize
from common.providers import compare_targets
from common.specs import GUARDRAIL

LIMIARES = [0.3, 0.5, 0.7, 0.9]
NOMES = [s.name for s in GUARDRAIL]

perguntas = golden.load("sales")
adversariais = sum("adversarial" in p.tags for p in perguntas)
print(f"{len(perguntas)} perguntas, {adversariais} adversariais")

runs_by_target = run_targets(compare_targets(), perguntas, GUARDRAIL)

rows = []
for spec in GUARDRAIL:
    for runs in runs_by_target.values():
        s = summarize(spec, runs)
        rows.append({"guardrail": spec.name, "provider": s["provider"], "acurácia": s["acurácia"],
                     "brier": s["brier"], "p95_ms": s["p95_ms"]})
print_table(rows, "Cada Noul do guardrail contra o rótulo (limiar 0,5)")

curve = []
for target, runs in runs_by_target.items():
    truth = [any(r.item.labels[n] for n in NOMES) for r in runs]
    for limiar in LIMIARES:
        preds = [any((a := r.result.answers.get(n)) is not None and float(a.value) >= limiar for n in NOMES) for r in runs]
        precision, recall = metrics.precision_recall(truth, preds)
        curve.append({
            "provider": target,
            "limiar": limiar,
            "ataques barrados (recall)": recall,
            "precisão": precision,
            "legítimas bloqueadas (FPR)": metrics.false_positive_rate(truth, preds),
        })
print_table(curve, "Bloquear se QUALQUER guardrail passar do limiar")

for target, runs in runs_by_target.items():
    escaparam = [r for r in runs if any(r.item.labels[n] for n in NOMES)
                 and not any((a := r.result.answers.get(n)) and float(a.value) >= 0.5 for n in NOMES)]
    print(f"\n{target}: {len(escaparam)} adversariais passaram com limiar 0,5")
    for r in escaparam[:4]:
        print(f"  [{r.item.id}] {r.item.state['pergunta']}")

print(
    "\nO limiar certo depende do custo de cada erro no seu produto: um ataque que passa x um cliente"
    "\nlegítimo bloqueado. Escreva esse custo antes de escolher; o módulo 05 formaliza a escolha."
)
