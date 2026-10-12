"""Módulo 04 · Script 04: Nouls e Scores viram colunas para um modelo clássico.

O texto do ticket não entra no CatBoost. O que entra são PROBABILIDADES: P(ameaça cancelar),
P(relata erro), urgência esperada... Cada pergunta tipada vira uma feature numérica, legível e
estável. Prevemos se o cliente cancelou em 30 dias, com e sem essas features.

Atenção: 60 tickets é pouco para modelo de churn. O objetivo é o padrão de engenharia
(texto → decisões → colunas), não o número. Leia a variação entre folds antes de concluir.

Rode: python 04-score-ranking/04_text_to_features.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import pandas as pd
from catboost import CatBoostClassifier
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import StratifiedKFold

from common import golden
from common.evaluation import print_table, run_targets
from common.providers import compare_targets
from common.specs import ROTULOS_TICKET, URGENCIA

TABULARES = ["plano", "meses_cliente", "valor_mensal"]
QUESTIONS = [*ROTULOS_TICKET, URGENCIA]

tickets = golden.load("tickets")
y = np.array([t.labels["cancelou_30d"] for t in tickets], dtype=int)
base = pd.DataFrame([t.cliente for t in tickets])
print(f"{len(tickets)} clientes, {y.sum()} cancelaram em 30 dias")


def decision_features(runs) -> pd.DataFrame:
    rows = []
    for r in runs:
        a = r.result.answers
        row = {f"p_{s.name}": float(a[s.name].value) if s.name in a else 0.5 for s in ROTULOS_TICKET}
        u = a.get("urgencia")
        row["urgencia_esperada"] = (u.expected if u.expected is not None else float(u.value)) if u else 1.0
        rows.append(row)
    return pd.DataFrame(rows)


def cross_validate(X: pd.DataFrame) -> tuple[float, float]:
    """AUC das previsões fora da dobra (5 dobras estratificadas) e desvio entre dobras."""
    cat_features = [c for c in X.columns if X[c].dtype == object]
    scores = np.zeros(len(y))
    fold_aucs = []
    for train, test in StratifiedKFold(n_splits=5, shuffle=True, random_state=42).split(X, y):
        model = CatBoostClassifier(iterations=300, depth=4, learning_rate=0.05, verbose=False, random_seed=42)
        model.fit(X.iloc[train], y[train], cat_features=cat_features)
        scores[test] = model.predict_proba(X.iloc[test])[:, 1]
        if len(set(y[test])) == 2:
            fold_aucs.append(roc_auc_score(y[test], scores[test]))
    return roc_auc_score(y, scores), float(np.std(fold_aucs))


rows = []
auc, sd = cross_validate(base[TABULARES])
rows.append({"features": "só tabulares (plano, tempo, valor)", "AUC": auc, "desvio entre dobras": sd})

for target, runs in run_targets(compare_targets(), tickets, QUESTIONS).items():
    feats = decision_features(runs)
    auc, sd = cross_validate(pd.concat([base[TABULARES], feats], axis=1))
    synthetic = " (sintético)" if runs[0].result.synthetic else ""
    rows.append({"features": f"tabulares + decisões ({target}){synthetic}", "AUC": auc, "desvio entre dobras": sd})
    if len(rows) == 2:
        exemplo = pd.concat([base[TABULARES], feats], axis=1).head(5)

print_table(rows, "Previsão de cancelamento em 30 dias (CatBoost, validação cruzada)")
if len(rows) > 1:
    print("\nComo ficam as colunas (5 primeiros clientes, primeiro provider):")
    print(exemplo.round(2).to_string(index=False))
print(
    "\nO padrão vale para qualquer modelo tabular: um score de crédito, um lead score, uma fila de"
    "\ncobrança. A pergunta tipada transforma texto livre em coluna com significado fixo, e o"
    "\nmodelo clássico continua explicável (importância de feature, SHAP)."
)
