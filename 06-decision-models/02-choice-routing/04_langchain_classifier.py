"""Módulo 02 · Script 04: o script 01 reescrito com o `TypeSafeClassifier` (langchain-typesafe).

Parte A: o classificador é um Runnable. `batch` paraleliza, callbacks funcionam e, com
LANGSMITH_TRACING=true e LANGSMITH_API_KEY no .env, cada chamada vira um trace com tokens.

Parte B: o middleware experimental `ModelRouterMiddleware` põe um Choice antes do modelo
num `create_agent`. Os modelos de chat aqui são falsos de propósito: o que interessa é qual
deles o roteador escolhe, não o texto que eles geram.

Rode: python 02-choice-routing/04_langchain_classifier.py
Para gravar contra o Laya: DECISION_TARGET=laya (o classificador aponta para o laya-serve).
"""

import itertools
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from langchain.agents import create_agent
from langchain_core.language_models.fake_chat_models import GenericFakeChatModel
from langchain_core.messages import AIMessage, HumanMessage

from common import golden, metrics
from common.providers import default_target
from common.providers.jev_langchain import make_classifier, to_langchain_questions
from common.providers.replay import is_live
from common.specs import FILA, ROTA

lc_target = "laya" if default_target() == "laya" else "jev-langchain"
classifier = make_classifier(lc_target)
print(f"Classificador: {classifier.model} em {classifier.base_url} ({'live' if is_live(lc_target) else 'replay'})")
if os.environ.get("LANGSMITH_TRACING") == "true" and os.environ.get("LANGSMITH_API_KEY"):
    print("LangSmith ligado: as chamadas aparecem como runs do tipo 'llm', com usage_metadata.\n")

# --- Parte A: Runnable + batch --------------------------------------------------------------
tickets = golden.load("tickets")
questions = to_langchain_questions([FILA])  # objetos Choice do langchain-typesafe
requests = [{"state": t.state, "questions": questions} for t in tickets]

responses = classifier.batch(requests, config={"max_concurrency": 8})
preds = [r.choices["fila"].choice for r in responses]
truth = [t.labels["fila"] for t in tickets]
tokens = sum(r.usage.input_tokens or 0 for r in responses)
print(f"Parte A: {len(tickets)} tickets em batch")
print(f"  acurácia {metrics.accuracy(truth, preds):.1%} | F1 macro {metrics.f1_macro(truth, preds):.1%} | {tokens} tokens de entrada no total")
print("  (o mesmo número do script 01 para este provider: é a mesma decisão por outra superfície)")

# --- Parte B: ModelRouterMiddleware ---------------------------------------------------------
from langchain_typesafe.experimental.middleware import ModelChoice, ModelRouterMiddleware

barato = GenericFakeChatModel(messages=itertools.cycle([AIMessage("[modelo barato] resposta padrão do suporte")]))
caro = GenericFakeChatModel(messages=itertools.cycle([AIMessage("[modelo caro] resposta investigada com cuidado")]))

if not is_live(lc_target) or lc_target == "laya":
    # O middleware cria um TypeSafeClassifier no __init__, que exige uma chave.
    # Em replay, nenhuma requisição sai da máquina; a chave é só para passar na validação.
    os.environ.setdefault("TYPESAFE_API_KEY", "replay")

router = ModelRouterMiddleware(
    choices={
        "barato": ModelChoice(model=barato, criteria=ROTA.criteria["barato"]),
        "caro": ModelChoice(model=caro, criteria=ROTA.criteria["caro"]),
    },
    instructions=ROTA.instructions,
)
router.classifier = make_classifier(lc_target)  # mesmo modo (replay/live/record) do resto do bloco
agent = create_agent(barato, middleware=[router])

print("\nParte B: create_agent com ModelRouterMiddleware")
amostra = [t for t in tickets if t.id in {"t-001", "t-005", "t-019", "t-021", "t-029", "t-040", "t-046", "t-058"}]
acertos = 0
for t in amostra:
    state = agent.invoke({"messages": [HumanMessage(t.state["ticket"])]})
    route = state["model_route"]
    acertos += route.choice == t.labels["rota"]
    print(f"  [{t.id}] rota={route.choice:<6} ({route.confidence:.2f}) esperado={t.labels['rota']:<6} → {state['messages'][-1].content}")
print(f"  {acertos}/{len(amostra)} rotas certas. A resposta completa (com probabilidades) fica em state['model_route'].")
