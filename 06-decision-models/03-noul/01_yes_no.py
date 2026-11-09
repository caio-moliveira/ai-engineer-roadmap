"""Aula 03 · Script 01: uma pergunta de sim ou não com um Noul.

"O cliente está pedindo reembolso?" O Noul devolve a probabilidade de a resposta ser sim.
O `criteria` descreve o que conta como sim e o que conta como não, e é ele que resolve os
casos de fronteira (o cliente que só reclama do preço não está pedindo dinheiro de volta).

Rode: python 06-decision-models/03-noul/01_yes_no.py
Precisa de TYPESAFE_API_KEY no .env da raiz.
"""

import os
import sys
import time

from dotenv import load_dotenv
from typesafe_sdk import Noul, TypeSafeClient

load_dotenv()
if not os.environ.get("TYPESAFE_API_KEY"):
    sys.exit("Defina TYPESAFE_API_KEY no .env da raiz para chamar o Jev.")

LIMIAR = 0.5

pede_reembolso = Noul(
    instructions="O cliente está pedindo reembolso ou estorno?",
    criteria={
        "true": "pede dinheiro de volta, estorno, cancelamento de cobrança ou crédito na fatura",
        "false": "só reclama, pergunta sobre preço ou pede outra coisa",
    },
)

MENSAGENS = [
    "Cobraram duas vezes no meu cartão, quero o valor de volta.",
    "O produto chegou quebrado. Não quero troca, quero meu dinheiro.",
    "Achei o plano caro demais para o que entrega.",
    "Como faço para emitir a segunda via do boleto?",
    "Se não resolverem até sexta, vou pedir o estorno no banco.",
]

with TypeSafeClient() as client:
    for mensagem in MENSAGENS:
        start = time.perf_counter()
        response = client.system_one(
            state={"mensagem": mensagem}, questions={"reembolso": pede_reembolso}
        )
        latency_ms = (time.perf_counter() - start) * 1000

        p_sim = response.nouls["reembolso"].noul
        decisao = "SIM" if p_sim >= LIMIAR else "não"
        print(f"\n{mensagem}")
        print(f"  P(sim) = {p_sim:.2f} {'█' * round(p_sim * 30):<30} → {decisao}")
        print(
            f"  [{response.usage.input_tokens} tokens de entrada, {latency_ms:.0f} ms]"
        )

print(
    "\nO Noul devolve um número só: a probabilidade de sim. A probabilidade de não é 1 - P(sim)."
    "\nA última mensagem é uma ameaça condicional: o cliente ainda não pediu. Veja onde ela cai."
    "\nSe o seu negócio trata ameaça como pedido, diga isso no `criteria`, não no limiar."
)
