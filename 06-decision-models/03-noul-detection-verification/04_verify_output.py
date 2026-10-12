"""Módulo 03 · Script 04: verificar a resposta DEPOIS do LLM.

O LLM gerou uma resposta a partir dos dados de vendas. Antes de mandar para o usuário:
- responde ao pedido?
- inventa algum número?
- segue a política (sem previsão, sem dado pessoal, sem recomendar punição)?

Três Nouls sobre o trio (pergunta, dados, resposta). O código aprova só se as três passarem.
Golden set: 24 respostas rotuladas à mão, boas e com defeitos plantados.

Rode: python 03-noul-detection-verification/04_verify_output.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from common import golden, metrics
from common.evaluation import print_table, run_targets, summarize
from common.providers import compare_targets
from common.specs import VERIFICACAO

LIMIAR = 0.5


def aprovar(answers) -> bool:
    def p(nome: str) -> float:
        a = answers.get(nome)
        return float(a.value) if a else 0.5

    return p("responde_pedido") >= LIMIAR and p("inventa_numero") < LIMIAR and p("segue_politica") >= LIMIAR


respostas = golden.load("verify")
truth = [i.labels["responde_pedido"] and not i.labels["inventa_numero"] and i.labels["segue_politica"] for i in respostas]
print(f"{len(respostas)} respostas; {sum(truth)} deveriam ser aprovadas")

runs_by_target = run_targets(compare_targets(), respostas, VERIFICACAO)

rows = []
for spec in VERIFICACAO:
    for runs in runs_by_target.values():
        s = summarize(spec, runs)
        rows.append({"verificação": spec.name, "provider": s["provider"], "acurácia": s["acurácia"], "brier": s["brier"]})
print_table(rows, "Cada verificação contra o rótulo")

final = []
for target, runs in runs_by_target.items():
    preds = [aprovar(r.result.answers) for r in runs]
    precision, recall = metrics.precision_recall([not t for t in truth], [not p for p in preds])
    final.append({
        "provider": target,
        "acurácia": metrics.accuracy(truth, preds),
        "defeitos barrados (recall)": recall,
        "precisão do bloqueio": precision,
        "tokens_in_médio": sum(r.result.tokens_in or 0 for r in runs) / len(runs),
        "custo_1k_usd": sum(r.result.cost_usd or 0 for r in runs) / len(runs) * 1000,
    })
print_table(final, "Decisão final: aprovar a resposta?")

if runs_by_target:
    target, runs = next(iter(runs_by_target.items()))
    print(f"\nDefeitos que passaram ({target}):")
    for r, ok in zip(runs, truth):
        if not ok and aprovar(r.result.answers):
            print(f"  [{r.item.id}] {r.item.tags} {r.item.state['resposta'][:90]}")

print(
    "\nO estado aqui é grande (a tabela de dados inteira). Com o Laya, o contexto padrão é de 1.024"
    "\ntokens por pergunta: confira `usage.truncated` na resposta crua antes de confiar no resultado."
)
