"""Módulo 03 · Script 01: "é spam?" é uma pergunta ou seis?

Duas formas de decidir:
- direta: um Noul "este e-mail é spam?";
- decomposta: seis Nouls verificáveis (pede credencial? urgência artificial? prêmio? remetente
  inconsistente? link suspeito? pede pagamento?) e uma soma ponderada EM CÓDIGO.

A decomposta é auditável: você sabe POR QUE um e-mail foi barrado, ajusta um peso sem
re-treinar nada e mede cada sinal contra o golden set separadamente.

Rode: python 03-noul-detection-verification/01_spam_decomposed.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from common import golden, metrics
from common.evaluation import print_table, run_targets, summarize
from common.providers import compare_targets
from common.specs import SINAIS_SPAM, SPAM_DIRETO

# Pesos da regra. São decisão de engenharia, não do modelo: versione e justifique.
PESOS = {
    "pede_credencial": 0.35,
    "link_suspeito": 0.25,
    "remetente_inconsistente": 0.20,
    "pede_pagamento": 0.15,
    "urgencia_artificial": 0.15,
    "promete_premio": 0.10,
}
LIMIAR_SPAM = 0.30


def score_decomposto(answers) -> float:
    return sum(peso * float(answers[nome].value) for nome, peso in PESOS.items() if nome in answers)


emails = golden.load("spam")
truth = [e.labels["spam"] for e in emails]
print(f"{len(emails)} e-mails: {sum(truth)} spam/golpe, {len(truth) - sum(truth)} legítimos")

direto = run_targets(compare_targets(), emails, [SPAM_DIRETO])
decomposto = run_targets(compare_targets(), emails, SINAIS_SPAM)

print_table([summarize(SPAM_DIRETO, runs) for runs in direto.values()], "Noul direto: 'é spam?'")

rows = []
for target, runs in decomposto.items():
    scores = [score_decomposto(r.result.answers) for r in runs]
    preds = [s >= LIMIAR_SPAM for s in scores]
    precision, recall = metrics.precision_recall(truth, preds)
    rows.append({
        "provider": target + (" (sintético)" if runs[0].result.synthetic else ""),
        "acurácia": metrics.accuracy(truth, preds),
        "precisão": precision,
        "recall": recall,
        "falso_positivo": metrics.false_positive_rate(truth, preds),
        "custo_1k_usd": sum(r.result.cost_usd or 0 for r in runs) / len(runs) * 1000,
    })
print_table(rows, f"Decomposto: 6 Nouls + soma ponderada (limiar {LIMIAR_SPAM})")

sinais = []
for spec in SINAIS_SPAM:
    for target, runs in decomposto.items():
        s = summarize(spec, runs)
        sinais.append({"sinal": spec.name, "provider": s["provider"], "acurácia": s["acurácia"], "brier": s["brier"]})
print_table(sinais, "Cada sinal medido separadamente contra o rótulo")

if decomposto:
    target, runs = next(iter(decomposto.items()))
    print(f"\nPor que cada e-mail foi barrado ({target}), três exemplos:")
    for r in [r for r in runs if score_decomposto(r.result.answers) >= LIMIAR_SPAM][:3]:
        acesos = {n: round(float(a.value), 2) for n in PESOS if (a := r.result.answers.get(n)) and float(a.value) >= 0.5}
        print(f"  [{r.item.id}] {r.item.state['assunto']!r} → score {score_decomposto(r.result.answers):.2f}, sinais: {acesos}")

print(
    "\nRepare nos legítimos difíceis do golden set (tag parece_phishing, cobranca_legitima):"
    "\numa cobrança real 'pede pagamento' e um aviso real de login 'parece urgente'. Um sinal sozinho"
    "\nnão decide; a combinação, com pesos que você controla, decide."
)
