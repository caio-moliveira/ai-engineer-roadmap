"""Aula 02 · Script 02: escolher a tool do agente com um Choice.

No function calling, o LLM lê a descrição de todas as tools e gera a chamada. Aqui, o catálogo
de tools vira o `criteria` de um Choice: o Jev escolhe a tool, e o código a executa.
A opção "nenhuma" cobre perguntas que nenhuma tool responde.

Rode: python 06-decision-models/02-choice/02_tool_selection.py
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

LIMIAR = 0.70


# As tools do agente de vendas. Aqui devolvem dados fixos; num sistema real, consultariam o banco.
def vendas_por_regiao() -> str:
    return "Sudeste R$ 4,2 mi | Sul R$ 1,9 mi | Nordeste R$ 1,1 mi"


def produtos_mais_vendidos() -> str:
    return "1. Fone Bluetooth  2. Carregador 65W  3. Smartwatch"


def status_do_pedido() -> str:
    return "Pedido 4821: enviado em 03/11, previsão de entrega 07/11"


def estoque_do_produto() -> str:
    return "Fone Bluetooth: 312 unidades no CD de Campinas"


TOOLS = {
    "vendas_por_regiao": (
        vendas_por_regiao,
        "faturamento total agrupado por região do país",
    ),
    "produtos_mais_vendidos": (
        produtos_mais_vendidos,
        "ranking dos produtos com mais unidades vendidas",
    ),
    "status_do_pedido": (
        status_do_pedido,
        "situação de entrega de um pedido específico",
    ),
    "estoque_do_produto": (
        estoque_do_produto,
        "quantidade disponível de um produto no estoque",
    ),
}

tool = Choice(
    instructions="Qual tool responde a pergunta do usuário?",
    criteria={nome: descricao for nome, (_, descricao) in TOOLS.items()}
    | {
        "nenhuma": "nenhuma das tools tem o dado pedido, ou a pergunta não é sobre vendas"
    },
)

PERGUNTAS = [
    "Qual região faturou mais este ano?",
    "Meu pedido 4821 já saiu para entrega?",
    "Ainda tem fone bluetooth disponível?",
    "Qual foi o produto campeão de vendas?",
    "Me passa o CPF dos clientes que mais compraram.",
    "Qual a previsão do tempo para amanhã?",
]

with TypeSafeClient() as client:
    for pergunta in PERGUNTAS:
        start = time.perf_counter()
        response = client.system_one(
            state={"pergunta": pergunta}, questions={"tool": tool}
        )
        latency_ms = (time.perf_counter() - start) * 1000

        answer = response.choices["tool"]
        print(f"\n{pergunta}")
        print(
            f"  tool: {answer.choice} ({answer.confidence:.2f})   [{response.usage.input_tokens} tokens, {latency_ms:.0f} ms]"
        )

        if answer.choice == "nenhuma":
            print("  → sem tool: o agente responde que não tem esse dado")
        elif answer.confidence < LIMIAR:
            print("  → confiança baixa: o agente pede para o usuário reformular")
        else:
            funcao, _ = TOOLS[answer.choice]
            print(f"  → {funcao()}")

print(
    "\nO que mudou em relação ao function calling:"
    "\n- Quem executa a tool é o seu código, a partir de uma escolha com probabilidade."
    "\n- O modelo não gera a chamada: não há argumento inventado nem nome de tool que não existe."
    "\n- Os argumentos (o número do pedido, o produto), quando precisar, vêm de outra etapa:"
    "\n  extração com LLM ou com código. O Choice resolve só a escolha."
    "\n- O pedido de CPF não deveria chegar até aqui. Barrar dado sensível é trabalho de um"
    "\n  guardrail antes da escolha de tool, com Nouls (Aula 3)."
)
