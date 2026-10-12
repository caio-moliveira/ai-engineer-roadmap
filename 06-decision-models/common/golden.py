"""Carrega os golden sets de `data/` (RF-05) num formato único.

Todo item tem `state` (o que o modelo vê) e `labels` (o gabarito), com os rótulos
nomeados igual às perguntas: o rótulo `fila` é a resposta certa da pergunta `fila`.
Esse contrato de nomes é o que permite medir qualquer provider com o mesmo código.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict

from common.decisions import canonical_json

DATA_DIR = Path(__file__).resolve().parents[1] / "data"

DATASETS = {
    "tickets": "golden_tickets.json",  # suporte de um SaaS: fila, categoria, urgência, rótulos
    "spam": "golden_spam.json",  # e-mails: spam e seis sinais verificáveis
    "rerank": "golden_rerank.json",  # perguntas sobre clima com 10 trechos candidatos cada
    "verify": "golden_verify.json",  # pergunta + dados + resposta do LLM, com rótulos de verificação
    "sales": "golden_sales.json",  # 80 perguntas de vendas do workshop-jev (tool + guardrail)
    "tool_calls": "golden_tool_calls.json",  # chamadas de tool para o gate de risco
}


class GoldenItem(BaseModel):
    model_config = ConfigDict(extra="allow")  # campos próprios de cada dataset (cliente, tool...)

    id: str
    state: dict[str, Any]
    labels: dict[str, Any]
    tags: list[str] = []
    difficulty: str | None = None


class RerankCandidate(BaseModel):
    id: str
    rank_retriever: int
    trecho: str
    relevancia: int


class RerankQuery(BaseModel):
    id: str
    pergunta: str
    candidatos: list[RerankCandidate]
    tags: list[str] = []


def _read(name: str) -> list[dict]:
    return json.loads((DATA_DIR / DATASETS[name]).read_text(encoding="utf-8"))


def _select(items: list[GoldenItem], tag: str | None, limit: int | None) -> list[GoldenItem]:
    if tag is not None:
        items = [i for i in items if tag in i.tags]
    return items[:limit] if limit else items


def load(name: str, tag: str | None = None, limit: int | None = None) -> list[GoldenItem]:
    """Carrega um golden set pelo nome curto (ver `DATASETS`)."""
    if name == "sales":
        items = [_sales_item(raw) for raw in _read("sales")]
    elif name == "rerank":
        items = rerank_pairs()
    elif name == "tool_calls":
        items = [
            GoldenItem(id=raw["id"], state={"mensagem": raw["mensagem"], "tool": raw["tool"], "args": raw["args"]},
                       labels=raw["labels"], tags=raw["tags"])
            for raw in _read("tool_calls")
        ]
    else:
        items = [GoldenItem.model_validate(raw) for raw in _read(name)]
    return _select(items, tag, limit)


def _sales_item(raw: dict) -> GoldenItem:
    """O golden set do workshop-jev guarda texto e rótulos em outro formato; adaptamos aqui."""
    return GoldenItem(
        id=raw["id"],
        state={"pergunta": raw["text"]},
        labels={"tool": raw["labels"]["tool"], **raw["guardrail"]},
        tags=raw["tags"],
        difficulty=raw["difficulty"],
    )


def load_rerank() -> list[RerankQuery]:
    return [RerankQuery.model_validate(raw) for raw in _read("rerank")]


def rerank_pairs() -> list[GoldenItem]:
    """Um item por par (pergunta, trecho): é o que o modelo de decisão pontua."""
    return [
        GoldenItem(
            id=c.id,
            state={"pergunta": q.pergunta, "trecho": c.trecho},
            labels={"relevancia": c.relevancia},
            tags=q.tags,
            query_id=q.id,
            rank_retriever=c.rank_retriever,
        )
        for q in load_rerank()
        for c in q.candidatos
    ]


def label_index() -> dict[str, dict[str, Any]]:
    """Estado canônico -> rótulos, juntando todos os golden sets."""
    index: dict[str, dict[str, Any]] = {}
    for name in DATASETS:
        for item in load(name):
            index.setdefault(canonical_json(item.state), {}).update(item.labels)
    return index


def summary() -> list[dict[str, Any]]:
    rows = []
    for name, filename in DATASETS.items():
        items = load(name)
        rows.append({"dataset": name, "arquivo": f"data/{filename}", "itens": len(items),
                     "rótulos": ", ".join(sorted(items[0].labels))})
    return rows
