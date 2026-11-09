"""Aula 04 · Script 02: rerank de trechos de um RAG com um Score.

O retriever do Bloco 2 devolve trechos por similaridade de embedding, e similaridade não é
relevância. Aqui, um Score dá a cada trecho uma nota de relevância para a pergunta numa rubrica
que você define, e a lista é reordenada pelo valor esperado.

Rode: python 06-decision-models/04-score/02_rerank.py
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

relevancia = Score(
    instructions="Quanto o trecho ajuda a responder a pergunta?",
    criteria=[
        "irrelevante: fala de outro assunto",
        "relacionado: mesmo tema, mas não responde",
        "parcial: responde parte da pergunta",
        "responde: o trecho contém a resposta",
    ],
)

PERGUNTA = "Qual o prazo para pedir reembolso de uma compra?"

# Na ordem em que o retriever devolveu: o primeiro é o mais parecido, não o mais útil.
TRECHOS = [
    "Reembolsos são processados em até 10 dias úteis após a aprovação, no mesmo meio de pagamento.",
    "Nossa política de reembolso foi atualizada em 2025 para atender ao Código de Defesa do Consumidor.",
    "O cliente pode solicitar o reembolso em até 7 dias corridos após o recebimento do produto.",
    "Para trocar um produto, acesse Meus Pedidos e clique em Solicitar troca.",
    "Compras feitas com cupom de desconto têm o reembolso calculado sobre o valor pago.",
    "O frete grátis vale para compras acima de R$ 199 nas regiões Sul e Sudeste.",
]

notas = []
tokens_in = latencia_total = 0.0
with TypeSafeClient() as client:
    for posicao, trecho in enumerate(TRECHOS, start=1):
        start = time.perf_counter()
        response = client.system_one(
            state={"pergunta": PERGUNTA, "trecho": trecho},
            questions={"relevancia": relevancia},
        )
        latency_ms = (time.perf_counter() - start) * 1000
        tokens_in += response.usage.input_tokens
        latencia_total += latency_ms
        notas.append((response.scores["relevancia"].score, posicao, trecho))

print(f"Pergunta: {PERGUNTA}\n")
print("Antes (ordem do retriever):")
for posicao, trecho in enumerate(TRECHOS, start=1):
    print(f"  {posicao}. {trecho}")

print("\nDepois do rerank (valor esperado da relevância, de 0 a 3):")
for nova, (score, posicao, trecho) in enumerate(sorted(notas, reverse=True), start=1):
    print(f"  {nova}. [{score:.2f}] (era {posicao}) {trecho}")

n = len(TRECHOS)
print(
    f"\n{n} trechos: {tokens_in:.0f} tokens de entrada no total, {latencia_total:.0f} ms somando as chamadas."
)
print(
    "\nConfira: o trecho que responde (7 dias) deveria subir para o topo, e o que só cita a"
    "\npolítica de reembolso, descer. No RAG, você manda ao LLM só os primeiros, ou só os de"
    "\nnota acima de 2."
    "\nEm produção, faça as chamadas em paralelo (cliente assíncrono do SDK) para a latência"
    "\nser a da chamada mais lenta, e não a soma."
)
