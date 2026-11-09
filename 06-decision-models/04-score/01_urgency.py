"""Aula 04 · Script 01: urgência de tickets numa rubrica ordenada, com um Score.

O Score posiciona o estado numa escala de níveis em ordem (0 = menos urgente). A resposta traz
a probabilidade de cada nível e o valor esperado (`score`): um número contínuo que serve para
ordenar a fila, mesmo entre tickets que caem no mesmo nível.

Rode: python 06-decision-models/04-score/01_urgency.py
Precisa de TYPESAFE_API_KEY no .env da raiz.
"""

import os
import sys
import time

from dotenv import load_dotenv
from typesafe_sdk import Score, TypeSafeClient

load_dotenv()
if not os.environ.get("TYPESAFE_API_KEY"):
    sys.exit("Defina TYPESAFE_API_KEY no .env da raiz para chamar o Jev.")

# A rubrica: a ordem importa. O nível 0 é o menos urgente.
NIVEIS = [
    "pode esperar: dúvida ou pedido sem prazo",
    "esta semana: problema que incomoda, mas tem contorno",
    "hoje: cliente bloqueado ou cobrado indevidamente",
    "agora: sistema fora do ar para muitos usuários ou risco de perda de dados",
]
urgencia = Score(
    instructions="Qual a urgência deste ticket de suporte?", criteria=NIVEIS
)

TICKETS = [
    "Vocês têm previsão de lançar o modo escuro?",
    "A exportação para CSV está lenta, mas termina.",
    "Fui cobrado duas vezes e o limite do meu cartão estourou.",
    "Ninguém da empresa consegue logar desde as 9h, o sistema inteiro está fora.",
    "Não consigo acessar minha conta e tenho uma apresentação para o cliente em uma hora.",
    "Gostaria de trocar o e-mail cadastrado na conta.",
]

resultados = []
with TypeSafeClient() as client:
    for ticket in TICKETS:
        start = time.perf_counter()
        response = client.system_one(
            state={"ticket": ticket}, questions={"urgencia": urgencia}
        )
        latency_ms = (time.perf_counter() - start) * 1000

        answer = response.scores["urgencia"]
        resultados.append((answer.score, ticket))

        print(f"\n{ticket}")
        print(
            f"  valor esperado: {answer.score:.2f}  (confiança {answer.confidence:.2f})"
        )
        for nivel, p in answer.probabilities.items():
            print(f"    nível {nivel}  {p:5.2f}  {'█' * round(p * 30)}")
        print(
            f"  [{response.usage.input_tokens} tokens de entrada, {latency_ms:.0f} ms]"
        )

print("\nFila ordenada pelo valor esperado (mais urgente primeiro):")
for score, ticket in sorted(resultados, reverse=True):
    print(f"  {score:4.2f}  {ticket}")

print(
    "\nPor que o valor esperado e não o nível mais provável:"
    "\n- Dois tickets no nível 2 não são iguais: um pode estar perto do 3, outro perto do 1."
    "\n- O valor esperado soma nível × probabilidade e desempata. É o número que ordena a fila."
)
