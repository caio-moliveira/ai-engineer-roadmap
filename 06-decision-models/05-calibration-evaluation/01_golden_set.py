"""Módulo 05 · Script 01: como montar, rotular e validar um golden set.

Golden set é o gabarito: exemplos rotulados que servem de verdade para medir qualquer
provider. Sem ele, "o Jev é melhor" ou "o LLM é melhor" é opinião.

O formato do bloco (data/golden_*.json), um item por exemplo:
    {
      "id": "t-001",                       # estável: fixtures e relatórios apontam para ele
      "state": {"ticket": "..."},          # exatamente o que o modelo vê
      "labels": {"fila": "financeiro"},    # uma chave por PERGUNTA, com o valor certo
      "tags": ["financeiro", "ambiguo"],   # para fatiar a métrica (adversarial, difícil...)
      "difficulty": "easy"
    }

Este script valida todos os golden sets contra as perguntas de common/specs.py e mostra
como eles estão distribuídos. Não chama nenhum modelo.

Rode: python 05-calibration-evaluation/01_golden_set.py
"""

import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from common import golden, specs
from common.evaluation import print_table

print_table(golden.summary(), "Golden sets do bloco")

# --- Validação: todo rótulo precisa ser um valor que a pergunta aceita -------------------
CHECKS = [
    ("tickets", specs.FILA), ("tickets", specs.CATEGORIA_FLAT), ("tickets", specs.URGENCIA), ("tickets", specs.ROTA),
    *[("tickets", s) for s in specs.ROTULOS_TICKET],
    ("spam", specs.SPAM_DIRETO), *[("spam", s) for s in specs.SINAIS_SPAM],
    ("sales", specs.TOOL), *[("sales", s) for s in specs.GUARDRAIL],
    *[("verify", s) for s in specs.VERIFICACAO], ("verify", specs.QUALIDADE),
    ("rerank", specs.RELEVANCIA),
]


def valid_values(spec):
    if spec.type == "choice":
        return set(spec.criteria)
    if spec.type == "score":
        return set(range(len(spec.criteria)))
    return {True, False}


problemas = 0
for dataset, spec in CHECKS:
    for item in golden.load(dataset):
        value = item.labels.get(spec.name)
        if value not in valid_values(spec):
            problemas += 1
            print(f"✗ {dataset}/{item.id}: rótulo {spec.name}={value!r} fora de {sorted(map(str, valid_values(spec)))}")
print(f"\nValidação: {len(CHECKS)} pares (golden set, pergunta), {problemas} problemas.")

# --- Distribuição: o que o golden set cobre e o que falta --------------------------------
tickets = golden.load("tickets")
print("\nTickets por fila e dificuldade:")
print(" ", dict(Counter((t.labels["fila"], t.difficulty) for t in tickets).most_common()))
print("Tickets ambíguos (rótulo discutível, onde a confiança deveria cair):",
      [t.id for t in tickets if "ambiguo" in t.tags])
spam = golden.load("spam")
print("E-mails legítimos difíceis:", [e.id for e in spam if not e.labels["spam"] and e.difficulty == "hard"])
sales = golden.load("sales")
print("Vendas adversariais por tipo:", dict(Counter(t for s in sales for t in s.tags if "adversarial" in s.tags and t != "adversarial")))

print(
    "\nReceita para o seu golden set:"
    "\n1. Tire exemplos do tráfego real (anonimizados), não invente só casos fáceis."
    "\n2. Rotule com duas pessoas uma amostra e meça a concordância (kappa, script 03 do módulo 04)."
    "\n   Se humanos não concordam, o modelo não tem como acertar: reescreva a pergunta."
    "\n3. Marque com tags os casos difíceis, ambíguos e adversariais: a média esconde exatamente eles."
    "\n4. Versione o arquivo. Mudou um rótulo, mudou a métrica: commit explícito (`data: ...`)."
    "\n5. Separe um pedaço para escolher limiares e outro para relatar o resultado (script 03)."
)
