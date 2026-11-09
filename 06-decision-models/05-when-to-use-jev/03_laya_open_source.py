"""Aula 05 · Script 03: o Laya, um modelo de decisão open source, com o mesmo código do Jev.

O Laya (Convai Innovations, licença Apache 2.0) roda na sua máquina e serve a mesma API do Jev
(`POST /v1/systemone`). Trocar de um para o outro é trocar a `base_url` do mesmo SDK.

Suba o Laya antes (da raiz do repositório):
    docker compose --profile decision up -d laya

Rode: python 06-decision-models/05-when-to-use-jev/03_laya_open_source.py
O Laya não precisa de chave. Com TYPESAFE_API_KEY no .env, o script também chama o Jev
e mostra os dois lado a lado.
"""

import os
import sys
import time

import httpx
from dotenv import load_dotenv
from typesafe_sdk import Choice, Noul, Score, TypeSafeClient

load_dotenv()

# No Windows, use 127.0.0.1 e não localhost (localhost tenta IPv6 primeiro e atrasa ~2 s).
LAYA_URL = os.environ.get("LAYA_BASE_URL", "http://127.0.0.1:8001")

try:
    httpx.get(f"{LAYA_URL}/health", timeout=5).raise_for_status()
except httpx.HTTPError:
    sys.exit(
        f"O Laya não responde em {LAYA_URL}. Suba com: docker compose --profile decision up -d laya"
    )

CLIENTES = {
    # O SDK exige uma chave não vazia; o Laya local aceita qualquer uma.
    "Laya (local)": lambda: TypeSafeClient(
        base_url=LAYA_URL, api_key="laya-local", model="multilingual"
    ),
}
if os.environ.get("TYPESAFE_API_KEY"):
    CLIENTES["Jev (API)"] = lambda: TypeSafeClient()
else:
    print("[sem TYPESAFE_API_KEY: só o Laya]\n")

TICKET = "Apareceram duas cobranças de R$ 89,90 no meu cartão no mesmo dia. Se não resolverem, vou cancelar."

# Os três tipos de pergunta numa chamada só, iguais para os dois modelos.
PERGUNTAS = {
    "fila": Choice(
        instructions="Qual fila deve atender este ticket de suporte?",
        criteria={
            "financeiro": "cobranças, estornos, notas fiscais, boletos e pagamentos",
            "tecnico": "erros no sistema, integrações, lentidão e exportação de dados",
            "comercial": "planos, preços, descontos, contratação e demonstrações",
            "conta": "senha e acesso, dados cadastrais, cancelamento, usuários e permissões",
        },
    ),
    "ameaca_cancelar": Noul(
        instructions="O cliente diz que vai cancelar ou trocar de fornecedor?"
    ),
    "urgencia": Score(
        instructions="Qual a urgência deste ticket?",
        criteria=["pode esperar", "resolver esta semana", "resolver hoje"],
    ),
}

print(f"Ticket: {TICKET}")
for nome, make_client in CLIENTES.items():
    with make_client() as client:
        client.system_one(
            state={"ticket": "aquecimento"}, questions={"x": Noul(instructions="ok?")}
        )
        start = time.perf_counter()
        response = client.system_one(state={"ticket": TICKET}, questions=PERGUNTAS)
        latency_ms = (time.perf_counter() - start) * 1000

    fila = response.choices["fila"]
    print(f"\n{nome}  (modelo: {response.model})")
    print(f"  fila:            {fila.choice} ({fila.confidence:.2f})")
    print(f"  ameaca_cancelar: P(sim) = {response.nouls['ameaca_cancelar'].noul:.2f}")
    print(f"  urgencia:        {response.scores['urgencia'].score:.2f} de 0 a 2")
    print(
        f"  [{response.usage.input_tokens} tokens de entrada, {response.usage.output_tokens} de saída, {latency_ms:.0f} ms]"
    )

print(
    "\nO que saber antes de usar o Laya:"
    "\n- Zero-shot, ele fica abaixo do Jev, principalmente em Score. Meça no seu caso antes de decidir."
    "\n- O checkpoint multilíngue sai sem calibração de fábrica (o próprio model card diz): a"
    "\n  confiança dele não é uma probabilidade confiável até você calibrar."
    "\n- A força dele é outra: roda na sua máquina, sem custo por chamada, sem o dado sair da"
    "\n  empresa, e pode ser ajustado (fine-tune) com os seus exemplos."
    "\n- A latência acima é de CPU local, sem rede. A do Jev inclui a ida e volta pela internet."
)
