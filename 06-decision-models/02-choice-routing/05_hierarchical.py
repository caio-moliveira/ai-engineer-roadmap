"""Módulo 02 · Script 05: classificação em dois níveis (fila → categoria), um Choice por nível.

Duas estratégias para chegar às 16 categorias:
- plana: um Choice com as 16 opções de uma vez;
- hierárquica: um Choice de fila (4 opções) e, dentro da fila escolhida, um Choice de categoria (4 opções).

A hierárquica faz duas chamadas, mas cada uma é mais fácil. O erro do primeiro nível se
propaga: se a fila estiver errada, a categoria certa nem está entre as opções.

Rode: python 02-choice-routing/05_hierarchical.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from common import golden, metrics
from common.evaluation import print_table
from common.providers import compare_targets, get_client
from common.providers.replay import ReplayMissError
from common.specs import CATEGORIA_FLAT, FILA, categoria_da_fila

tickets = golden.load("tickets")
truth = [t.labels["categoria"] for t in tickets]
rows = []

for target in compare_targets():
    client = get_client(target)
    try:
        flat = [client.decide(t.state, [CATEGORIA_FLAT]) for t in tickets]
        nivel1 = [client.decide(t.state, [FILA]) for t in tickets]
        nivel2 = [
            client.decide(t.state, [categoria_da_fila(r.answers["fila"].value)])
            if r.answers.get("fila") and r.answers["fila"].value in FILA.criteria
            else None
            for t, r in zip(tickets, nivel1)
        ]
    except ReplayMissError as error:
        print(f"⚠️  pulando '{target}': {str(error).splitlines()[0]}")
        continue

    flat_pred = [r.answers["categoria"].value if "categoria" in r.answers else None for r in flat]
    hier_pred = [r.answers["categoria"].value if r and "categoria" in r.answers else None for r in nivel2]
    fila_ok = [r.answers.get("fila") and r.answers["fila"].value == t.labels["fila"] for r, t in zip(nivel1, tickets)]
    synthetic = " (sintético)" if flat[0].synthetic else ""

    def latency(results):
        return metrics.p95([sum(r.latency_ms for r in rs if r) for rs in results])

    rows.append({"provider": target + synthetic, "estratégia": "plana (16 opções)", "chamadas": 1,
                 "acurácia": metrics.accuracy(truth, flat_pred), "f1_macro": metrics.f1_macro(truth, flat_pred),
                 "p95_ms": latency([[r] for r in flat]),
                 "custo_1k_usd": sum(r.cost_usd or 0 for r in flat) / len(flat) * 1000})
    rows.append({"provider": target + synthetic, "estratégia": "hierárquica (4 + 4)", "chamadas": 2,
                 "acurácia": metrics.accuracy(truth, hier_pred), "f1_macro": metrics.f1_macro(truth, hier_pred),
                 "p95_ms": latency([[a, b] for a, b in zip(nivel1, nivel2)]),
                 "custo_1k_usd": sum((a.cost_usd or 0) + ((b.cost_usd or 0) if b else 0) for a, b in zip(nivel1, nivel2)) / len(tickets) * 1000})
    perdidos = sum(1 for ok in fila_ok if not ok)
    print(f"{target}: {perdidos} tickets já saem do nível 1 na fila errada (a categoria certa não está nas opções do nível 2)")

print_table(rows, "Categoria: plana x hierárquica")
print(
    "\nQuando preferir a hierárquica: muitas opções (o Laya, por exemplo, perde acurácia acima de ~20"
    "\nopções por pergunta), hierarquia natural no domínio, ou quando o nível 1 sozinho já decide algo"
    "\n(qual time atende). Quando preferir a plana: poucas opções e latência apertada."
)
