"""Módulo 01 · Script 02: a primeira chamada pelo SDK oficial (`typesafe-sdk`).

Um `Choice`: escolher uma opção de uma lista. O SDK valida as perguntas antes de enviar,
faz retry, e devolve objetos tipados: `response.choices["fila"].choice`.

Rode: python 01-decision-fundamentals/02_sdk_first_call.py [jev|laya]
Em replay, o SDK roda de verdade; só o transporte HTTP responde a partir da gravação.
"""

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from typesafe_sdk import Choice

from common.providers.jev_sdk import make_typesafe_client
from common.providers.replay import is_live

target = sys.argv[1] if len(sys.argv) > 1 else "jev"

ticket = "Fui cobrado duas vezes na fatura de setembro. Preciso que estornem o valor duplicado ainda hoje."

fila = Choice(
    instructions="Qual fila deve atender este ticket de suporte?",
    criteria={
        "financeiro": "cobranças, estornos, notas fiscais, boletos e pagamentos",
        "tecnico": "erros no sistema, integrações, lentidão e exportação de dados",
        "comercial": "planos, preços, descontos, contratação e demonstrações",
        "conta": "senha e acesso, dados cadastrais, cancelamento, usuários e permissões",
    },
)

with make_typesafe_client(target) as client:
    start = time.perf_counter()
    response = client.system_one(state={"ticket": ticket}, questions={"fila": fila})
    elapsed = (time.perf_counter() - start) * 1000

answer = response.choices["fila"]
print(f"Ticket: {ticket}\n")
print(f"modelo:    {response.model}")
print(f"escolha:   {answer.choice}")
print(f"confiança: {answer.confidence:.3f}")
print("probabilidades:")
for label, p in sorted(answer.probabilities.items(), key=lambda kv: -kv[1]):
    print(f"  {label:<11} {p:6.3f}  {'█' * round(p * 40)}")
print(f"\ntokens de entrada: {response.usage.input_tokens}, de saída: {response.usage.output_tokens}")
if is_live(target):
    print(f"latência: {elapsed:.0f} ms")
else:
    print("latência: replay, sem rede (a latência original está na fixture e aparece no script 03)")

print(
    "\nRepare: a resposta não é um texto que diz 'financeiro'. É uma distribuição sobre as quatro"
    "\nfilas. A `confidence` é o que permite decidir em código: acima do limiar, automatiza;"
    "\nabaixo, manda para um humano. O módulo 05 mostra como escolher esse limiar com dados."
)
