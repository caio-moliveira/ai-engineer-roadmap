"""Aula 01 · Script 02: a mesma decisão no Jev, no GPT-5.6 Luna e no Claude Sonnet 5.5.

Três tickets, uma pergunta: qual fila atende? O Jev responde com uma distribuição. Os LLMs
respondem com structured output (JSON validado por Pydantic), o jeito comum de fazer isso hoje.
Para cada chamada, medimos tokens (vindos da resposta da API) e latência (relógio).

Rode: python 06-decision-models/01-decision-fundamentals/02_jev_vs_llm.py
Usa TYPESAFE_API_KEY, OPENAI_API_KEY e ANTHROPIC_API_KEY. Um provedor sem chave é pulado.
"""

import os
import time
from typing import Literal

from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from pydantic import BaseModel, Field
from typesafe_sdk import Choice, TypeSafeClient

load_dotenv()

TICKETS = [
    "Fui cobrado duas vezes na fatura de setembro. Preciso que estornem o valor duplicado.",
    "A exportação para CSV trava em 99% desde a atualização de ontem. Não estou gostando do sistema e quero reembolso do valor pago.",
    "Quero saber se existe desconto no plano anual para ONGs. Se não houver quero cancelar minha assinatura e receber o reembolso do valor pago.",
]

FILAS = {
    "financeiro": "cobranças, estornos, notas fiscais, boletos e pagamentos",
    "tecnico": "erros no sistema, integrações, lentidão e exportação de dados",
    "comercial": "planos, preços, descontos, contratação e demonstrações",
    "conta": "senha e acesso, dados cadastrais, cancelamento, usuários e permissões",
}
PERGUNTA = "Qual fila deve atender este ticket de suporte?"


# --- Jev: estado + pergunta tipada -----------------------------------------------------------
def ask_jev(ticket: str) -> dict:
    with TypeSafeClient() as client:
        start = time.perf_counter()
        response = client.system_one(
            state={"ticket": ticket},
            questions={"fila": Choice(instructions=PERGUNTA, criteria=FILAS)},
        )
        latency_ms = (time.perf_counter() - start) * 1000
    answer = response.choices["fila"]
    return {
        "fila": answer.choice,
        "probabilidades": dict(answer.probabilities),
        "tokens_in": response.usage.input_tokens,
        "tokens_out": response.usage.output_tokens,
        "latency_ms": latency_ms,
    }


# --- LLM: prompt + structured output ---------------------------------------------------------
class Probabilidades(BaseModel):
    financeiro: float = Field(description="Probabilidade da fila financeiro, de 0 a 1.")
    tecnico: float = Field(description="Probabilidade da fila tecnico, de 0 a 1.")
    comercial: float = Field(description="Probabilidade da fila comercial, de 0 a 1.")
    conta: float = Field(description="Probabilidade da fila conta, de 0 a 1.")


class Decisao(BaseModel):
    fila: Literal["financeiro", "tecnico", "comercial", "conta"]
    probabilidades: Probabilidades = Field(
        description="Probabilidade de cada fila atender o ticket; as quatro devem somar 1."
    )


def ask_llm(model: str, ticket: str) -> dict:
    llm = init_chat_model(model).with_structured_output(
        Decisao, method="json_schema", include_raw=True
    )
    filas = "\n".join(f"- {nome}: {descricao}" for nome, descricao in FILAS.items())
    prompt = f"{PERGUNTA}\n\nFilas:\n{filas}\n\nTicket: {ticket}"

    start = time.perf_counter()
    output = llm.invoke(prompt)
    latency_ms = (time.perf_counter() - start) * 1000

    usage = output["raw"].usage_metadata or {}
    return {
        "fila": output["parsed"].fila,
        "probabilidades": output["parsed"].probabilidades.model_dump(),
        "tokens_in": usage.get("input_tokens", 0),
        "tokens_out": usage.get("output_tokens", 0),
        "latency_ms": latency_ms,
    }


PROVEDORES = {
    "Jev": ("TYPESAFE_API_KEY", ask_jev),
    "GPT-6 Luna": ("OPENAI_API_KEY", lambda t: ask_llm("openai:gpt-6-luna", t)),
    "Claude Sonnet 5.5": (
        "ANTHROPIC_API_KEY",
        lambda t: ask_llm("anthropic:claude-sonnet-5-5", t),
    ),
}

resultados: dict[str, list[dict]] = {}
for nome, (chave, ask) in PROVEDORES.items():
    if not os.environ.get(chave):
        print(f"[pulando {nome}: defina {chave} no .env]")
        continue
    try:
        resultados[nome] = [ask(t) for t in TICKETS]
    except Exception as error:  # um provedor fora do ar não derruba a comparação
        print(f"[{nome} falhou: {type(error).__name__}: {str(error)[:120]}]")

for i, ticket in enumerate(TICKETS):
    print(f"\nTicket {i + 1}: {ticket}")
    colunas_filas = " ".join(f"{fila:>10}" for fila in FILAS)
    print(
        f"  {'provedor':<18} {'escolha':<11} {colunas_filas} {'soma':>6}"
        f" {'tok. entrada':>13} {'tok. saída':>11} {'latência':>10}"
    )
    for nome, runs in resultados.items():
        r = runs[i]
        probs = r["probabilidades"]
        valores_filas = " ".join(f"{probs.get(fila, 0):>10.1%}" for fila in FILAS)
        print(
            f"  {nome:<18} {r['fila']:<11} {valores_filas} {sum(probs.values()):>6.2f}"
            f" {r['tokens_in']:>13} {r['tokens_out']:>11} {r['latency_ms']:>8.0f} ms"
        )

if resultados:
    print("\nMédia por chamada:")
    print(
        f"  {'provedor':<18} {'tok. entrada':>13} {'tok. saída':>11} {'latência':>10}"
    )
    for nome, runs in resultados.items():
        n = len(runs)
        print(
            f"  {nome:<18} {sum(r['tokens_in'] for r in runs) / n:>13.0f} "
            f"{sum(r['tokens_out'] for r in runs) / n:>11.0f} {sum(r['latency_ms'] for r in runs) / n:>8.0f} ms"
        )

print(
    "\nO que observar:"
    "\n- Tokens de saída: o LLM gera o JSON token a token; o modelo de decisão não gera texto."
    "\n- Probabilidades: no Jev, são a distribuição que o modelo calcula sobre as quatro filas"
    "\n  (a soma é sempre 1). No LLM, são números que ele escreveu no JSON, tão gerados quanto"
    "\n  o resto: a soma pode não fechar em 1 e não dá para usá-los como probabilidade de verdade."
    "\n- Tokens de entrada: a pergunta e as opções entram nos dois casos. O prompt do LLM ainda"
    "\n  carrega as instruções de formato que o structured output acrescenta."
)
