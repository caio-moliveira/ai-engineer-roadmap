"""Módulo 01 · Script 04: o mesmo código contra o Laya, rodando na sua máquina.

O Laya (Convai Innovations, Apache 2.0) serve o mesmo `POST /v1/systemone` do Jev.
Trocar de provider é trocar a `base_url`: o SDK, as perguntas e o parse ficam iguais.

Suba o servidor (escolha um):
    docker compose --profile decision up laya          # da raiz do repositório
    uv run laya-serve                                   # com LAYA_PORT=8001 LAYA_MODELS=multilingual

Rode: python 01-decision-fundamentals/04_laya_local.py
Em replay, não precisa do servidor: a resposta vem da gravação feita com o Laya real.
"""

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import httpx
from typesafe_sdk import Choice, Noul, Score

from common.providers.jev_sdk import LAYA_BASE_URL, make_typesafe_client
from common.providers.replay import is_live

base_url = os.environ.get("LAYA_BASE_URL") or LAYA_BASE_URL

if is_live("laya"):
    try:
        health = httpx.get(f"{base_url}/health", timeout=5).json()
    except httpx.HTTPError:
        sys.exit(f"Laya não responde em {base_url}. Suba com: docker compose --profile decision up laya")
    print(f"Laya em {base_url}: checkpoints carregados {health.get('loaded')}, device {health.get('device')}\n")
else:
    print(f"[replay] sem chamar {base_url}; respostas gravadas com o Laya real.\n")

ticket = "Apareceram duas cobranças de R$ 89,90 no meu cartão no mesmo dia. Se não resolverem, vou cancelar a assinatura."
questions = {
    "fila": Choice(
        instructions="Qual fila deve atender este ticket de suporte?",
        criteria={
            "financeiro": "cobranças, estornos, notas fiscais, boletos e pagamentos",
            "tecnico": "erros no sistema, integrações, lentidão e exportação de dados",
            "comercial": "planos, preços, descontos, contratação e demonstrações",
            "conta": "senha e acesso, dados cadastrais, cancelamento, usuários e permissões",
        },
    ),
    "ameaca_cancelar": Noul(instructions="O cliente diz que vai cancelar, sair ou migrar para outro fornecedor?"),
    "urgencia": Score(
        instructions="Qual a urgência deste ticket?",
        criteria=["pode esperar", "resolver esta semana", "resolver hoje"],
    ),
}

# A única linha que muda em relação ao Jev: o cliente aponta para outro servidor.
with make_typesafe_client("laya") as client:
    response = client.system_one(state={"ticket": ticket}, questions=questions)

print(f"modelo: {response.model}  |  tokens de entrada: {response.usage.input_tokens}\n")
print(f"fila            → {response.choices['fila'].choice} (confiança {response.choices['fila'].confidence:.2f})")
print(f"ameaca_cancelar → P(sim) = {response.nouls['ameaca_cancelar'].noul:.2f}")
score = response.scores["urgencia"]
print(f"urgencia        → {score.score:.2f} (nível mais provável: {max(score.probabilities, key=score.probabilities.get)})")
print(f"                  distribuição: {dict(score.probabilities)}")

raw = response.raw_http_response.json()
if "routing" in raw:
    print(f"\nO Laya conta qual checkpoint usou: {raw['routing'].get('model')} ({raw['routing'].get('reason')})")

print(
    "\nO que o curso precisa dizer em voz alta sobre o Laya:"
    "\n- Zero-shot, fica bem abaixo do Jev em benchmarks independentes. O módulo 05 mede no nosso golden set."
    "\n- O checkpoint multilíngue sai sem calibração (o próprio model card diz). Não confie no 0,99 antes de medir."
    "\n- Contexto de 1.024 tokens por pergunta por padrão: estados longos precisam ser fatiados."
    "\n- A tese do Laya é ajustar nos seus dados (fine-tune), não usá-lo zero-shot."
)
