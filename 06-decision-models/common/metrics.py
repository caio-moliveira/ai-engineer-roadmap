"""Métricas do bloco (RF-06). Python puro, de propósito: dá para ler cada fórmula.

Convenções:
- `y_true` e `y_pred` são listas de rótulos (str, int ou bool).
- `confidences` são números de 0 a 1: a confiança do provider na resposta que ele deu.
- `correct` é uma lista de bool: a resposta bateu com o golden set?
"""

from __future__ import annotations

import math
from collections.abc import Sequence
from dataclasses import dataclass


def _check_same_len(*seqs: Sequence) -> int:
    lengths = {len(s) for s in seqs}
    if len(lengths) != 1:
        raise ValueError(f"sequências com tamanhos diferentes: {sorted(lengths)}")
    n = lengths.pop()
    if n == 0:
        raise ValueError("sequência vazia")
    return n


# ---------------------------------------------------------------------------
# Classificação
# ---------------------------------------------------------------------------


def accuracy(y_true: Sequence, y_pred: Sequence) -> float:
    n = _check_same_len(y_true, y_pred)
    return sum(t == p for t, p in zip(y_true, y_pred, strict=True)) / n


def f1_macro(y_true: Sequence, y_pred: Sequence, labels: Sequence | None = None) -> float:
    """Média do F1 de cada classe. Classe sem nenhum exemplo nem previsão fica de fora."""
    _check_same_len(y_true, y_pred)
    labels = list(labels) if labels is not None else sorted(set(y_true) | set(y_pred), key=str)
    scores = []
    for label in labels:
        tp = sum(t == label and p == label for t, p in zip(y_true, y_pred, strict=True))
        fp = sum(t != label and p == label for t, p in zip(y_true, y_pred, strict=True))
        fn = sum(t == label and p != label for t, p in zip(y_true, y_pred, strict=True))
        if tp + fp + fn == 0:
            continue
        scores.append(2 * tp / (2 * tp + fp + fn))
    return sum(scores) / len(scores) if scores else 0.0


def precision_recall(y_true: Sequence[bool], y_pred: Sequence[bool]) -> tuple[float, float]:
    """Precisão e recall da classe positiva (True)."""
    _check_same_len(y_true, y_pred)
    tp = sum(t and p for t, p in zip(y_true, y_pred, strict=True))
    fp = sum((not t) and p for t, p in zip(y_true, y_pred, strict=True))
    fn = sum(t and (not p) for t, p in zip(y_true, y_pred, strict=True))
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    return precision, recall


def false_positive_rate(y_true: Sequence[bool], y_pred: Sequence[bool]) -> float:
    _check_same_len(y_true, y_pred)
    negatives = [p for t, p in zip(y_true, y_pred, strict=True) if not t]
    return sum(negatives) / len(negatives) if negatives else 0.0


# ---------------------------------------------------------------------------
# Probabilidade e calibração
# ---------------------------------------------------------------------------


def brier_binary(probs: Sequence[float], y_true: Sequence[bool]) -> float:
    """Erro quadrático médio entre P(verdadeiro) e o rótulo (0 ou 1). Menor é melhor."""
    n = _check_same_len(probs, y_true)
    return sum((p - float(t)) ** 2 for p, t in zip(probs, y_true, strict=True)) / n


def brier_multiclass(distributions: Sequence[dict], y_true: Sequence, labels: Sequence) -> float:
    """Brier multiclasse: soma, por classe, de (p - 1[classe certa])², média nos exemplos.

    Vai de 0 (perfeito) a 2. Exige distribuição completa: LLM sem probabilidades não entra.
    """
    n = _check_same_len(distributions, y_true)
    total = 0.0
    for dist, truth in zip(distributions, y_true, strict=True):
        total += sum((dist.get(str(label), 0.0) - (1.0 if str(label) == str(truth) else 0.0)) ** 2 for label in labels)
    return total / n


@dataclass
class ReliabilityBin:
    lower: float
    upper: float
    count: int
    mean_confidence: float
    accuracy: float


def reliability_bins(confidences: Sequence[float], correct: Sequence[bool], n_bins: int = 10) -> list[ReliabilityBin]:
    """Agrupa as respostas por faixa de confiança e mede a acurácia de cada faixa."""
    _check_same_len(confidences, correct)
    bins = []
    for i in range(n_bins):
        lower, upper = i / n_bins, (i + 1) / n_bins
        members = [
            (c, ok)
            for c, ok in zip(confidences, correct, strict=True)
            if (lower <= c < upper) or (i == n_bins - 1 and c == 1.0)
        ]
        if members:
            mean_conf = sum(c for c, _ in members) / len(members)
            acc = sum(ok for _, ok in members) / len(members)
        else:
            mean_conf = acc = 0.0
        bins.append(ReliabilityBin(lower, upper, len(members), mean_conf, acc))
    return bins


def ece(confidences: Sequence[float], correct: Sequence[bool], n_bins: int = 10) -> float:
    """Expected Calibration Error: distância média entre confiança e acurácia, por faixa.

    Calibrado é: entre cem respostas com 74% de confiança, cerca de 74 estão certas.
    ECE 0 é calibração perfeita.
    """
    n = _check_same_len(confidences, correct)
    return sum(b.count / n * abs(b.mean_confidence - b.accuracy) for b in reliability_bins(confidences, correct, n_bins))


# ---------------------------------------------------------------------------
# Concordância
# ---------------------------------------------------------------------------


def agreement(a: Sequence, b: Sequence) -> float:
    """Fração de exemplos em que dois avaliadores deram a mesma resposta."""
    return accuracy(a, b)


def cohen_kappa(a: Sequence, b: Sequence) -> float:
    """Concordância corrigida pelo acaso. 1 = total, 0 = o que o acaso daria."""
    n = _check_same_len(a, b)
    observed = agreement(a, b)
    labels = set(a) | set(b)
    expected = sum((list(a).count(label) / n) * (list(b).count(label) / n) for label in labels)
    if expected == 1:
        return 1.0
    return (observed - expected) / (1 - expected)


# ---------------------------------------------------------------------------
# Latência e custo
# ---------------------------------------------------------------------------


def percentile(values: Sequence[float], q: float) -> float:
    """Percentil com interpolação linear (mesmo método padrão do numpy)."""
    if not values:
        raise ValueError("sequência vazia")
    if not 0 <= q <= 100:
        raise ValueError("q deve estar entre 0 e 100")
    ordered = sorted(values)
    pos = (len(ordered) - 1) * q / 100
    low, high = math.floor(pos), math.ceil(pos)
    if low == high:
        return float(ordered[low])
    return ordered[low] + (ordered[high] - ordered[low]) * (pos - low)


def p50(values: Sequence[float]) -> float:
    return percentile(values, 50)


def p95(values: Sequence[float]) -> float:
    return percentile(values, 95)


# ---------------------------------------------------------------------------
# Limiar e automação
# ---------------------------------------------------------------------------


@dataclass
class AutomationPoint:
    threshold: float
    automated: int  # respostas com confiança >= limiar (o sistema decide sozinho)
    total: int
    coverage: float  # automated / total
    accuracy: float | None  # acurácia só no subconjunto automatizado


def automation_curve(
    confidences: Sequence[float], correct: Sequence[bool], thresholds: Sequence[float]
) -> list[AutomationPoint]:
    """Para cada limiar: quanto você automatiza e com que acurácia.

    Abaixo do limiar, a decisão vai para um humano (ou para um modelo maior).
    """
    n = _check_same_len(confidences, correct)
    points = []
    for t in thresholds:
        kept = [ok for c, ok in zip(confidences, correct, strict=True) if c >= t]
        acc = sum(kept) / len(kept) if kept else None
        points.append(AutomationPoint(t, len(kept), n, len(kept) / n, acc))
    return points


def best_threshold(points: Sequence[AutomationPoint], min_accuracy: float) -> AutomationPoint | None:
    """Menor limiar (maior automação) que ainda entrega a acurácia mínima pedida."""
    ok = [p for p in points if p.accuracy is not None and p.accuracy >= min_accuracy]
    return max(ok, key=lambda p: (p.coverage, -p.threshold)) if ok else None


# ---------------------------------------------------------------------------
# Ranking
# ---------------------------------------------------------------------------


def recall_at_k(ranked_ids: Sequence[str], relevant_ids: set[str], k: int) -> float:
    if not relevant_ids:
        raise ValueError("sem itens relevantes: recall indefinido")
    return len(set(ranked_ids[:k]) & relevant_ids) / len(relevant_ids)


def dcg_at_k(grades: Sequence[float], k: int) -> float:
    return sum((2**g - 1) / math.log2(i + 2) for i, g in enumerate(grades[:k]))


def ndcg_at_k(ranked_grades: Sequence[float], k: int) -> float:
    """nDCG@k: o DCG da sua ordem dividido pelo DCG da ordem ideal."""
    ideal = dcg_at_k(sorted(ranked_grades, reverse=True), k)
    return dcg_at_k(ranked_grades, k) / ideal if ideal > 0 else 0.0
