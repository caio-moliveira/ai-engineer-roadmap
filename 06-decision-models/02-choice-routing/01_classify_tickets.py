"""Módulo 02 · Script 01: um Choice com 4 filas sobre o golden set de tickets.

Mede, por provider: acurácia, F1 macro, Brier, ECE, latência p50/p95 e custo por mil decisões.
Mesma `DecisionSpec` para todos (common/specs.py: FILA).

Rode: python 02-choice-routing/01_classify_tickets.py
Escolha os alvos com DECISION_TARGETS=jev,laya,llm:anthropic:claude-haiku-4-5-20251001
"""

import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from common import golden
from common.evaluation import prediction, print_table, run_targets, summarize
from common.providers import compare_targets
from common.specs import FILA

tickets = golden.load("tickets")
print(f"{len(tickets)} tickets | distribuição real: {dict(Counter(t.labels['fila'] for t in tickets))}")
print(f"Pergunta: {FILA.instructions}")
for label, desc in FILA.criteria.items():
    print(f"  - {label}: {desc}")

runs_by_target = run_targets(compare_targets(), tickets, [FILA])
print_table([summarize(FILA, runs) for runs in runs_by_target.values()], "Choice 'fila' por provider")

for target, runs in runs_by_target.items():
    erros = [r for r in runs if prediction(FILA, r) != r.item.labels["fila"]]
    print(f"\nErros de {target} ({len(erros)}):")
    for r in erros[:6]:
        a = r.result.answers.get("fila")
        conf = f"{a.confidence:.2f}" if a and a.confidence is not None else "—"
        print(f"  [{r.item.id}] previu {a.value if a else '—'} ({conf}), era {r.item.labels['fila']}: {r.item.state['ticket'][:80]}")

print(
    "\nRepare nos erros: muitos estão em tickets marcados como `ambiguo` no golden set"
    "\n(ex.: acesso bloqueado por falta de pagamento é financeiro ou conta?). A confiança"
    "\nnesses casos deveria ser menor: é o que o módulo 05 transforma em limiar."
)
