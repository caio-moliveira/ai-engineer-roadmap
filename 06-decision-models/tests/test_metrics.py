import math

import pytest

from common import metrics


def test_accuracy_e_f1_macro():
    y_true = ["a", "a", "b", "b"]
    y_pred = ["a", "b", "b", "b"]
    assert metrics.accuracy(y_true, y_pred) == 0.75
    # F1(a) = 2*1/(2*1+0+1) = 2/3 ; F1(b) = 2*2/(2*2+1+0) = 4/5
    assert metrics.f1_macro(y_true, y_pred) == pytest.approx((2 / 3 + 4 / 5) / 2)


def test_tamanhos_diferentes_falham():
    with pytest.raises(ValueError):
        metrics.accuracy([1, 2], [1])


def test_brier_binario():
    assert metrics.brier_binary([1.0, 0.0], [True, False]) == 0
    assert metrics.brier_binary([0.5, 0.5], [True, False]) == 0.25


def test_brier_multiclasse():
    dist = [{"a": 0.7, "b": 0.3}]
    # (0.7-1)^2 + (0.3-0)^2 = 0.09 + 0.09
    assert metrics.brier_multiclass(dist, ["a"], ["a", "b"]) == pytest.approx(0.18)


def test_ece_perfeito_e_superconfiante():
    # 10 respostas com 80% de confiança, 8 certas: calibrado
    assert metrics.ece([0.8] * 10, [True] * 8 + [False] * 2) == pytest.approx(0.0)
    # 10 respostas com 90% de confiança, 5 certas: ECE 0,4
    assert metrics.ece([0.9] * 10, [True] * 5 + [False] * 5) == pytest.approx(0.4)


def test_confianca_1_cai_no_ultimo_bin():
    bins = metrics.reliability_bins([1.0], [True], n_bins=10)
    assert bins[-1].count == 1


def test_kappa():
    assert metrics.cohen_kappa(["a", "b", "a", "b"], ["a", "b", "a", "b"]) == 1
    # concordância observada 0,5 com marginais 50/50: kappa 0
    assert metrics.cohen_kappa(["a", "a", "b", "b"], ["a", "b", "a", "b"]) == pytest.approx(0.0)


def test_percentis_como_numpy():
    values = [10, 20, 30, 40, 100]
    assert metrics.p50(values) == 30
    assert metrics.p95(values) == pytest.approx(88.0)


def test_curva_de_automacao():
    confs = [0.95, 0.9, 0.7, 0.6]
    correct = [True, True, False, True]
    points = metrics.automation_curve(confs, correct, [0.5, 0.85, 0.99])
    assert [p.coverage for p in points] == [1.0, 0.5, 0.0]
    assert points[0].accuracy == 0.75
    assert points[1].accuracy == 1.0
    assert points[2].accuracy is None
    best = metrics.best_threshold(points, min_accuracy=0.9)
    assert best.threshold == 0.85


def test_ranking():
    assert metrics.recall_at_k(["x", "y", "z"], {"y", "w"}, 2) == 0.5
    assert metrics.ndcg_at_k([2, 1, 0], 3) == pytest.approx(1.0)
    worse = metrics.ndcg_at_k([0, 1, 2], 3)
    assert 0 < worse < 1
    ideal = (3 / math.log2(2)) + (1 / math.log2(3))
    assert metrics.dcg_at_k([2, 1], 2) == pytest.approx(ideal)
