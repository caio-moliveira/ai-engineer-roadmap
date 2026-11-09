"""Aula 02 · Script 01: rotear tickets de suporte com um Choice.

Cada ticket recebe a probabilidade de cada fila. O código usa a confiança para decidir:
acima do limiar, encaminha sozinho; abaixo, manda para um humano revisar.

Rode: python 06-decision-models/02-choice/01_ticket_routing.py
Precisa de TYPESAFE_API_KEY no .env da raiz.
"""

import os
import sys
import time

from dotenv import load_dotenv
from typesafe_sdk import Choice, TypeSafeClient

load_dotenv()
if not os.environ.get("TYPESAFE_API_KEY"):
    sys.exit("Defina TYPESAFE_API_KEY no .env da raiz para chamar o Jev.")

LIMIAR = 0.80  # abaixo disso, um humano revisa

TICKETS = [
    "Fui cobrado duas vezes na fatura de setembro. Preciso do estorno.",
    "A integração com o ERP parou de sincronizar os pedidos desde ontem.",
    "Quanto custa o plano Empresarial para 50 usuários?",
    "Esqueci a senha e o e-mail de recuperação não chega.",
    "Quero cancelar a assinatura porque a nota fiscal veio com o CNPJ errado.",
    "Vocês atendem aos sábados?",
]

fila = Choice(
    instructions="Qual fila deve atender este ticket de suporte?",
    criteria={
        "financeiro": "cobranças, estornos, notas fiscais, boletos e pagamentos",
        "tecnico": "erros no sistema, integrações, lentidão e exportação de dados",
        "comercial": "planos, preços, descontos, contratação e demonstrações",
        "conta": "senha e acesso, dados cadastrais, cancelamento, usuários e permissões",
    },
)

tokens_in = latencia_total = 0.0
with TypeSafeClient() as client:
    for ticket in TICKETS:
        start = time.perf_counter()
        response = client.system_one(state={"ticket": ticket}, questions={"fila": fila})
        latency_ms = (time.perf_counter() - start) * 1000
        tokens_in += response.usage.input_tokens
        latencia_total += latency_ms

        answer = response.choices["fila"]
        destino = answer.choice if answer.confidence >= LIMIAR else "revisão humana"
        outras = {k: p for k, p in answer.probabilities.items() if k != answer.choice}
        segunda = max(outras.items(), key=lambda kv: kv[1])

        print(f"\n{ticket}")
        print(
            f"  {answer.choice} ({answer.confidence:.2f}), segunda opção: {segunda[0]} ({segunda[1]:.2f})"
        )
        print(
            f"  → {destino}   [{response.usage.input_tokens} tokens de entrada, {latency_ms:.0f} ms]"
        )

n = len(TICKETS)
print(
    f"\n{n} tickets: {tokens_in / n:.0f} tokens de entrada e {latencia_total / n:.0f} ms por decisão, em média."
)
print(
    "\nRepare nos tickets ambíguos (cancelamento por nota fiscal errada, pergunta sobre horário):"
    "\na probabilidade se divide entre filas e a confiança cai. É isso que o limiar captura."
    "\nUm LLM com structured output devolveria uma fila só, sem mostrar a dúvida."
)
