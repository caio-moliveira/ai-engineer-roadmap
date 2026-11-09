"""Aula 01 · Script 01: a primeira decisão com o Jev.

Mandamos um ticket de suporte (o "estado") e uma pergunta tipada (um Choice com quatro filas).
O Jev não escreve um texto dizendo "financeiro": devolve a probabilidade de cada fila.

Rode: python 06-decision-models/01-decision-fundamentals/01_first_decision.py
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

ticket = "Fui cobrado duas vezes na fatura de setembro. Preciso que estornem o valor duplicado ainda hoje."

# A pergunta: qual fila atende o ticket? As opções e o que cada uma significa ficam no `criteria`.
fila = Choice(
    instructions="Qual fila deve atender este ticket de suporte?",
    criteria={
        "financeiro": "cobranças, estornos, notas fiscais, boletos e pagamentos",
        "tecnico": "erros no sistema, integrações, lentidão e exportação de dados",
        "comercial": "planos, preços, descontos, contratação e demonstrações",
        "conta": "senha e acesso, dados cadastrais, cancelamento, usuários e permissões",
    },
)

# O cliente lê TYPESAFE_API_KEY do ambiente.
with TypeSafeClient() as client:
    start = time.perf_counter()
    response = client.system_one(state={"ticket": ticket}, questions={"fila": fila})
    latency_ms = (time.perf_counter() - start) * 1000

answer = response.choices["fila"]

print(f"Ticket: {ticket}\n")
print(f"modelo:    {response.model}")
print(f"escolha:   {answer.choice}")
print(f"confiança: {answer.confidence:.3f}\n")
print("probabilidade de cada fila:")
for label, p in sorted(answer.probabilities.items(), key=lambda kv: -kv[1]):
    print(f"  {label:<11} {p:6.3f}  {'█' * round(p * 40)}")

print(f"\ntokens de entrada: {response.usage.input_tokens}")
print(f"tokens de saída:   {response.usage.output_tokens}")
print(f"latência:          {latency_ms:.0f} ms")

print(
    "\nRepare: a resposta é uma distribuição sobre as quatro filas, e as probabilidades somam 1."
    "\nCom ela, o seu código decide: confiança alta, encaminha sozinho; baixa, chama um humano."
)
