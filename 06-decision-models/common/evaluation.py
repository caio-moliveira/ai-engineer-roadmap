"""Roda um provider sobre um golden set e resume o resultado de uma pergunta.

Todos os módulos medem do mesmo jeito: tokens da resposta, latência do relógio,
preço de `pricing.yaml`. Nada estimado.
"""

from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import dataclass
from typing import Any

from tabulate import tabulate

from common import metrics
from common.decisions import DecisionClient, DecisionResult, DecisionSpec
from common.golden import GoldenItem


@dataclass
class Run:
    item: GoldenItem
    result: DecisionResult


def run(
    client: DecisionClient,
    items: Sequence[GoldenItem],
    questions: list[DecisionSpec],
    state_fn: Callable[[GoldenItem], Any] | None = None,
    progress: bool = True,
) -> list[Run]:
    runs = []
    for i, item in enumerate(items, 1):
        state = state_fn(item) if state_fn else item.state
        runs.append(Run(item, client.decide(state, questions)))
        if progress and len(items) > 10 and i % 20 == 0:
            print(f"  [{client.provider}] {i}/{len(items)}")
    return runs


def run_targets(
    targets: Sequence[str],
    items: Sequence[GoldenItem],
    questions: list[DecisionSpec],
    state_fn: Callable[[GoldenItem], Any] | None = None,
) -> dict[str, list[Run]]:
    """Roda vários alvos. Alvo sem gravação (em replay) é pulado com aviso, não derruba o script."""
    from common.providers import get_client
    from common.providers.replay import ReplayMissError

    out: dict[str, list[Run]] = {}
    for target in targets:
        try:
            out[target] = run(get_client(target), items, questions, state_fn)
        except ReplayMissError as error:
            print(f"\n⚠️  pulando '{target}': {str(error).splitlines()[0]}")
    return out


def _answer(r: Run, name: str):
    return r.result.answers.get(name)


def prediction(spec: DecisionSpec, r: Run, threshold: float = 0.5):
    """O valor decidido (rótulo, nível ou bool), ou None se o provider não respondeu."""
    a = _answer(r, spec.name)
    if a is None:
        return None
    if spec.type == "noul":
        return float(a.value) >= threshold
    return a.value


def confidence(spec: DecisionSpec, r: Run) -> float | None:
    """Confiança na decisão tomada. Para noul, a distância de P(verdadeiro) até a dúvida."""
    a = _answer(r, spec.name)
    if a is None:
        return None
    if spec.type == "noul":
        p = float(a.value)
        return max(p, 1 - p)
    if a.confidence is not None:
        return float(a.confidence)
    if a.probabilities:
        return max(a.probabilities.values())
    return None


def summarize(spec: DecisionSpec, runs: Sequence[Run], threshold: float = 0.5) -> dict[str, Any]:
    """Acurácia, F1, Brier, ECE, latência, custo e falhas de formato de uma pergunta."""
    truth = [r.item.labels[spec.name] for r in runs]
    preds = [prediction(spec, r, threshold) for r in runs]
    confs = [confidence(spec, r) for r in runs]
    correct = [p == t for p, t in zip(preds, truth, strict=True)]
    results = [r.result for r in runs]

    row: dict[str, Any] = {
        "provider": results[0].provider + (" (sintético)" if any(x.synthetic for x in results) else ""),
        "n": len(runs),
        "acurácia": metrics.accuracy(truth, preds),
        "f1_macro": metrics.f1_macro(truth, preds),
    }

    if spec.type == "noul":
        probs = [float(r.result.answers[spec.name].value) if spec.name in r.result.answers else 0.5 for r in runs]
        row["brier"] = metrics.brier_binary(probs, truth)
    elif all(r.result.answers.get(spec.name) and r.result.answers[spec.name].probabilities for r in runs):
        labels = list(spec.criteria) if spec.type == "choice" else list(range(len(spec.criteria)))
        dists = [r.result.answers[spec.name].probabilities for r in runs]
        row["brier"] = metrics.brier_multiclass(dists, truth, labels)
    else:
        row["brier"] = None  # LLM: sem distribuição, sem Brier

    valid = [(c, ok) for c, ok in zip(confs, correct, strict=True) if c is not None]
    row["ece"] = metrics.ece([c for c, _ in valid], [ok for _, ok in valid]) if valid else None

    latencies = [x.latency_ms for x in results]
    row["p50_ms"] = metrics.p50(latencies)
    row["p95_ms"] = metrics.p95(latencies)
    costs = [x.cost_usd or 0.0 for x in results]
    row["custo_1k_usd"] = sum(costs) / len(costs) * 1000
    row["tokens_in_médio"] = sum(x.tokens_in or 0 for x in results) / len(results)
    row["falha_formato"] = sum((not x.parse_ok) or (not x.values_in_schema) for x in results)
    return row


def automation_inputs(spec: DecisionSpec, runs: Sequence[Run], threshold: float = 0.5):
    """(confianças, acertos) prontos para `metrics.automation_curve`."""
    pairs = []
    for r in runs:
        c = confidence(spec, r)
        if c is None:
            continue
        pairs.append((c, prediction(spec, r, threshold) == r.item.labels[spec.name]))
    return [c for c, _ in pairs], [ok for _, ok in pairs]


PCT_HINTS = ("acurácia", "f1", "cobertura", "precisão", "recall", "concordância", "fpr", "falso_positivo", "automatiz")


def print_table(rows: list[dict[str, Any]], title: str | None = None) -> None:
    if title:
        print(f"\n{title}")
    formatted = []
    for row in rows:
        out = {}
        for k, v in row.items():
            if v is None:
                out[k] = "—"
            elif isinstance(v, float):
                if any(hint in k.lower() for hint in PCT_HINTS):
                    out[k] = f"{v:.1%}"
                elif k.endswith("_ms") or "tokens" in k:
                    out[k] = f"{v:,.0f}"
                elif k.endswith("_usd"):
                    out[k] = f"{v:.4f}"
                else:
                    out[k] = f"{v:.3f}"
            else:
                out[k] = v
        formatted.append(out)
    print(tabulate(formatted, headers="keys", tablefmt="github"))
