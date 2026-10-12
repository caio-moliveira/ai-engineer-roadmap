"""Módulo 03 · Script 02: multirrótulo com um Noul por rótulo.

Um ticket pode pedir reembolso E ameaçar cancelar ao mesmo tempo. Um Choice obriga a
escolher um só; quatro Nouls dão quatro probabilidades independentes.

Rode: python 03-noul-detection-verification/02_multilabel.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from common import golden
from common.decisions import DecisionSpec
from common.evaluation import print_table, run_targets, summarize
from common.providers import compare_targets
from common.specs import ROTULOS_TICKET

NOMES = [s.name for s in ROTULOS_TICKET]

ASSUNTO_PRINCIPAL = DecisionSpec(
    name="assunto_principal",
    type="choice",
    instructions="Qual destas situações melhor descreve o ticket?",
    criteria={
        "pede_reembolso": "o cliente pede dinheiro de volta",
        "ameaca_cancelar": "o cliente diz que vai cancelar, sair ou migrar",
        "relata_erro": "o cliente relata algo que não funciona",
        "pede_informacao": "o cliente faz uma pergunta para obter informação",
        "nenhuma": "nenhuma das anteriores",
    },
)

tickets = golden.load("tickets")
multi = sum(1 for t in tickets if sum(t.labels[n] for n in NOMES) >= 2)
print(f"{len(tickets)} tickets; {multi} têm dois ou mais rótulos verdadeiros ao mesmo tempo.")


def set_f1(truth: set, pred: set) -> float:
    if not truth and not pred:
        return 1.0
    inter = len(truth & pred)
    return 2 * inter / (len(truth) + len(pred)) if truth or pred else 0.0


nouls = run_targets(compare_targets(), tickets, ROTULOS_TICKET)
choices = run_targets(compare_targets(), tickets, [ASSUNTO_PRINCIPAL])

rows = []
for target in nouls:
    for spec in ROTULOS_TICKET:
        s = summarize(spec, nouls[target])
        rows.append({"rótulo": spec.name, "provider": s["provider"], "acurácia": s["acurácia"], "f1_macro": s["f1_macro"], "brier": s["brier"]})
print_table(rows, "Cada rótulo como um Noul independente")

comp = []
for target in nouls:
    truth_sets = [{n for n in NOMES if r.item.labels[n]} for r in nouls[target]]
    noul_sets = [{n for n in NOMES if (a := r.result.answers.get(n)) and float(a.value) >= 0.5} for r in nouls[target]]
    row = {"provider": target, "F1 por ticket (4 Nouls)": sum(map(set_f1, truth_sets, noul_sets)) / len(tickets)}
    if target in choices:
        choice_sets = [
            {a.value} - {"nenhuma"} if (a := r.result.answers.get("assunto_principal")) else set() for r in choices[target]
        ]
        row["F1 por ticket (1 Choice)"] = sum(map(set_f1, truth_sets, choice_sets)) / len(tickets)
        row["exatos (Choice)"] = sum(t == c for t, c in zip(truth_sets, choice_sets))
    row["exatos (Nouls)"] = sum(t == n for t, n in zip(truth_sets, noul_sets))
    comp.append(row)
print_table(comp, "Conjunto de rótulos por ticket: Nouls x Choice")

print(
    "\nO Choice nunca acerta exatamente um ticket com dois rótulos: ele só pode devolver um."
    "\nUse Choice quando as opções são mutuamente exclusivas (fila, categoria) e Nouls quando"
    "\nas afirmações são independentes (sinais, rótulos, verificações)."
)
