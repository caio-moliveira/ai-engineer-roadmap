"""Módulo 01 · Script 01: a chamada HTTP crua, sem SDK.

Um modelo de decisão é só um endpoint: `POST /v1/systemone` com um estado e perguntas
tipadas. A resposta é uma distribuição de probabilidade por pergunta. Não há texto gerado
para parsear. Jev e Laya falam exatamente este esquema.

Rode (da pasta 06-decision-models):
    python 01-decision-fundamentals/01_http_direct.py          # Jev
    python 01-decision-fundamentals/01_http_direct.py laya     # Laya local
Em replay (padrão), a resposta vem da gravação; com DECISION_PROVIDER=live, vai para a rede.
"""

import json
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # para importar `common`

import httpx

from common.decisions import DecisionResult, answers_from_systemone, request_key
from common.pricing import cost_usd
from common.providers.jev_sdk import JEV_BASE_URL, JEV_MODEL, LAYA_BASE_URL, LAYA_MODEL
from common.providers.replay import is_live, is_recording, load_fixture, write_fixture

target = sys.argv[1] if len(sys.argv) > 1 else "jev"

# O estado pode ser texto, um objeto JSON ou uma lista. Aqui, um ticket de suporte.
state = {"ticket": "Apareceram duas cobranças de R$ 89,90 no meu cartão no mesmo dia. Se não resolverem, vou cancelar a assinatura."}

# As três perguntas tipadas, já no formato de fio.
questions = {
    "fila": {
        "type": "choice",
        "instructions": "Qual fila deve atender este ticket de suporte?",
        "criteria": {
            "financeiro": "cobranças, estornos, notas fiscais, boletos e pagamentos",
            "tecnico": "erros no sistema, integrações, lentidão e exportação de dados",
            "comercial": "planos, preços, descontos, contratação e demonstrações",
            "conta": "senha e acesso, dados cadastrais, cancelamento, usuários e permissões",
        },
    },
    "ameaca_cancelar": {
        "type": "noul",
        "instructions": "O cliente diz que vai cancelar, sair ou migrar para outro fornecedor?",
    },
    "urgencia": {
        "type": "score",
        "instructions": "Qual a urgência deste ticket?",
        "criteria": ["pode esperar", "resolver esta semana", "resolver hoje"],
    },
}

if target == "laya":
    base_url = os.environ.get("LAYA_BASE_URL") or LAYA_BASE_URL
    api_key, model = os.environ.get("LAYA_API_KEY") or "laya-local", LAYA_MODEL
else:
    base_url = os.environ.get("TYPESAFE_BASE_URL") or JEV_BASE_URL
    api_key, model = os.environ.get("TYPESAFE_API_KEY", ""), os.environ.get("JEV_MODEL") or JEV_MODEL

body = {"state": state, "model": model, "questions": questions}
print(f"POST {base_url}/v1/systemone")
print("Authorization: Bearer ****")
print(json.dumps(body, ensure_ascii=False, indent=2))

key = request_key(state, questions)
if is_live(target):
    start = time.perf_counter()
    response = httpx.post(
        f"{base_url}/v1/systemone",
        json=body,
        headers={"Authorization": f"Bearer {api_key}"},
        timeout=30,
    )
    latency_ms = (time.perf_counter() - start) * 1000
    response.raise_for_status()
    raw = response.json()
    if is_recording(target):
        usage = raw.get("usage") or {}
        result = DecisionResult(
            provider=target, model=raw["model"], answers=answers_from_systemone(raw["answers"]),
            latency_ms=latency_ms, tokens_in=usage.get("input_tokens"), tokens_out=usage.get("output_tokens"),
            cost_usd=cost_usd(raw["model"], usage.get("input_tokens"), usage.get("output_tokens")), raw=raw,
        )
        write_fixture(target, key, {"state": state, "questions": questions}, result.model_dump(mode="json"),
                      origin=f"httpx -> {base_url}")
else:
    fixture = load_fixture(target, key)
    raw, latency_ms = fixture["result"]["raw"], fixture["result"]["latency_ms"]
    print(f"\n[replay] resposta gravada em {fixture['recorded_at']} ({fixture['origin']})")

print(f"\n← {latency_ms:.0f} ms")
print(json.dumps(raw, ensure_ascii=False, indent=2))

print("\nO que olhar na resposta:")
print("- choice devolve `choice`, `confidence` e `probabilities` de TODAS as opções.")
print("- noul devolve só `noul`: a probabilidade de a afirmação ser verdadeira.")
print("- score devolve `score` (média ponderada dos níveis) e a distribuição por nível.")
print("- `usage` traz tokens de entrada; a saída de um modelo de decisão quase não consome tokens.")
