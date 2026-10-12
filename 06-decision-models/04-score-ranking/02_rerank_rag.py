"""Módulo 04 · Script 02: Score de relevância como reranker de RAG.

Pergunta-chave: o que o Cohere faz que você não consegue definir numa rubrica?

Cada pergunta do golden set tem 10 trechos candidatos, na ordem em que o retriever vetorial
os devolveu (o mesmo tema do PDF do Bloco 2, mudança climática). Um Score de relevância em
três níveis pontua cada par (pergunta, trecho); reordenamos pelo valor esperado e medimos
recall@5 e nDCG@5 contra a ordem original do retriever.

Rode: python 04-score-ranking/02_rerank_rag.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from common import golden, metrics
from common.evaluation import print_table, run_targets
from common.providers import compare_targets
from common.specs import RELEVANCIA

K = 5
queries = golden.load_rerank()
pares = golden.rerank_pairs()
print(f"{len(queries)} perguntas x 10 candidatos = {len(pares)} pares (pergunta, trecho)")


def avaliar(ordem_por_query: dict[str, list]) -> dict:
    recalls, ndcgs = [], []
    for q in queries:
        ordenados = ordem_por_query[q.id]
        relevantes = {c.id for c in q.candidatos if c.relevancia == 2}
        recalls.append(metrics.recall_at_k([c.id for c in ordenados], relevantes, K))
        ndcgs.append(metrics.ndcg_at_k([c.relevancia for c in ordenados], K))
    return {f"recall@{K}": sum(recalls) / len(recalls), f"nDCG@{K}": sum(ndcgs) / len(ndcgs)}


rows = [{"ordenação": "retriever vetorial (sem rerank)",
         **avaliar({q.id: sorted(q.candidatos, key=lambda c: c.rank_retriever) for q in queries}),
         "p95_ms por par": None, "custo por pergunta (US$)": 0.0}]

runs_by_target = run_targets(compare_targets(), pares, [RELEVANCIA])
for target, runs in runs_by_target.items():
    nota = {}
    for r in runs:
        a = r.result.answers.get("relevancia")
        nota[r.item.id] = (a.expected if a.expected is not None else float(a.value)) if a else 0.0
    ordem = {q.id: sorted(q.candidatos, key=lambda c: (-nota[c.id], c.rank_retriever)) for q in queries}
    synthetic = " (sintético)" if runs[0].result.synthetic else ""
    rows.append({
        "ordenação": f"rerank com Score ({target}){synthetic}",
        **avaliar(ordem),
        "p95_ms por par": metrics.p95([r.result.latency_ms for r in runs]),
        "custo por pergunta (US$)": sum(r.result.cost_usd or 0 for r in runs) / len(queries),
    })
print_table(rows, "Rerank: ordem do retriever x Score de relevância")

print(
    "\nO rerank custa uma chamada por candidato (aqui, 10 por pergunta). Com modelo de decisão,"
    "\nisso é barato e rápido; com LLM, é a parte cara do pipeline. Repare também que o Score"
    "\npermite mudar o que é 'relevante' editando a rubrica, sem treinar um cross-encoder novo."
)
