"""Aula 01 · Script 03: a mesma decisão em quatro modelos de decisão.

Jev (TypeSafe), Laya (open source, local), Gemini Decision 1 (Google) e Decisions API (OpenAI).
Três tickets, uma pergunta: qual fila atende? Os quatro devolvem uma probabilidade por fila,
sem gerar texto. O que muda é o nome dos campos, a resposta e o tempo de cada um.

Rode: python 06-decision-models/01-decision-fundamentals/03_decision_models.py
Usa TYPESAFE_API_KEY, GEMINI_API_KEY e OPENAI_API_KEY. Um provedor sem chave é pulado.
O Laya não precisa de chave, mas precisa estar no ar (da raiz do repositório):
    docker compose --profile decision up -d laya
"""

import os
import time

import httpx
from dotenv import load_dotenv
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

# No Windows, use 127.0.0.1 e não localhost (localhost tenta IPv6 primeiro e atrasa ~2 s).
LAYA_URL = os.environ.get("LAYA_BASE_URL", "http://127.0.0.1:8001")


# --- Jev e Laya: o mesmo SDK e o mesmo código, só muda a base_url ----------------------------
def ask_typesafe(client: TypeSafeClient, ticket: str) -> dict:
    with client:
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
        "tokens_in": response.usage.input_tokens or 0,
        "tokens_out": response.usage.output_tokens or 0,
        "latency_ms": latency_ms,
    }


def ask_jev(ticket: str) -> dict:
    return ask_typesafe(TypeSafeClient(), ticket)


def ask_laya(ticket: str) -> dict:
    # O SDK exige uma chave não vazia; o Laya local aceita qualquer uma.
    client = TypeSafeClient(
        base_url=LAYA_URL, api_key="laya-local", model="multilingual"
    )
    return ask_typesafe(client, ticket)


def laya_no_ar() -> bool:
    try:
        httpx.get(f"{LAYA_URL}/health", timeout=3).raise_for_status()
        return True
    except httpx.HTTPError:
        return False


# --- Gemini Decision 1: `input` no lugar de `state`; a pergunta é igual à do Jev -------------
# Chamamos a API por HTTP: as versões do SDK fixadas no repositório ainda não têm `decisions`.
def ask_gemini(ticket: str) -> dict:
    body = {
        "model": "gemini-decision-1",
        "input": ticket,
        "questions": {
            "fila": {"type": "choice", "instructions": PERGUNTA, "criteria": FILAS}
        },
    }
    start = time.perf_counter()
    response = httpx.post(
        "https://generativelanguage.googleapis.com/v1beta/decisions",
        headers={"x-goog-api-key": os.environ["GEMINI_API_KEY"]},
        json=body,
        timeout=60,
    )
    latency_ms = (time.perf_counter() - start) * 1000
    response.raise_for_status()
    data = response.json()
    answer = data["answers"]["fila"]
    return {
        "fila": answer["choice"],
        "probabilidades": answer["probabilities"],
        "tokens_in": data["usage"]["total_input_tokens"],
        "tokens_out": data["usage"]["total_output_tokens"],
        "latency_ms": latency_ms,
    }


# --- OpenAI Decisions API: perguntas em lista, opções em `choices` ---------------------------
def ask_openai(ticket: str) -> dict:
    body = {
        "model": "gpt-6-luna",
        "input": ticket,
        "questions": [
            {
                "type": "choice",
                "name": "fila",
                "instructions": PERGUNTA,
                "choices": [
                    {"value": nome, "description": descricao}
                    for nome, descricao in FILAS.items()
                ],
            }
        ],
    }
    start = time.perf_counter()
    response = httpx.post(
        "https://api.openai.com/v1/decisions",
        headers={"Authorization": f"Bearer {os.environ['OPENAI_API_KEY']}"},
        json=body,
        timeout=60,
    )
    latency_ms = (time.perf_counter() - start) * 1000
    response.raise_for_status()
    data = response.json()
    answer = data["answers"][0]
    return {
        "fila": answer["choice"],
        # A OpenAI devolve uma lista de {value, probability}; viramos dicionário como os outros.
        "probabilidades": {
            p["value"]: p["probability"] for p in answer["probabilities"]
        },
        "tokens_in": data["usage"]["input_tokens"],
        "tokens_out": data["usage"]["output_tokens"],
        "latency_ms": latency_ms,
    }


# nome -> (está disponível?, o que fazer se não estiver, função que pergunta)
PROVEDORES = {
    "Jev": (
        lambda: bool(os.environ.get("TYPESAFE_API_KEY")),
        "defina TYPESAFE_API_KEY no .env",
        ask_jev,
    ),
    "Laya (local)": (
        laya_no_ar,
        "suba com: docker compose --profile decision up -d laya",
        ask_laya,
    ),
    "Gemini Decision 1": (
        lambda: bool(os.environ.get("GEMINI_API_KEY")),
        "defina GEMINI_API_KEY no .env",
        ask_gemini,
    ),
    "OpenAI Decisions": (
        lambda: bool(os.environ.get("OPENAI_API_KEY")),
        "defina OPENAI_API_KEY no .env",
        ask_openai,
    ),
}

resultados: dict[str, list[dict]] = {}
for nome, (disponivel, como_resolver, ask) in PROVEDORES.items():
    if not disponivel():
        print(f"[pulando {nome}: {como_resolver}]")
        continue
    try:
        ask(
            "aquecimento"
        )  # a primeira chamada abre a conexão (e, no Laya, carrega o modelo)
        resultados[nome] = [ask(t) for t in TICKETS]
    except Exception as error:  # um provedor fora do ar não derruba a comparação
        print(f"[{nome} falhou: {type(error).__name__}: {str(error)[:160]}]")

for i, ticket in enumerate(TICKETS):
    print(f"\nTicket {i + 1}: {ticket}")
    colunas_filas = " ".join(f"{fila:>10}" for fila in FILAS)
    print(
        f"  {'provedor':<18} {'escolha':<11} {colunas_filas}"
        f" {'tok. entrada':>13} {'tok. saída':>11} {'latência':>10}"
    )
    for nome, runs in resultados.items():
        r = runs[i]
        probs = r["probabilidades"]
        valores_filas = " ".join(f"{probs.get(fila, 0):>10.1%}" for fila in FILAS)
        print(
            f"  {nome:<18} {r['fila']:<11} {valores_filas}"
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
    "\n- Mesma ideia, nomes diferentes: `state` no Jev e no Laya, `input` no Gemini e na OpenAI;"
    "\n  `criteria` no Jev, no Laya e no Gemini, `choices` na OpenAI. Compare as funções acima."
    "\n- Resposta: os quatro devolvem a distribuição completa sobre as filas, e a soma é 1."
    "\n  Nos tickets fáceis eles concordam; nos ambíguos, a distribuição de cada um difere."
    "\n- Tempo: Jev, Gemini e OpenAI incluem a ida e volta pela internet. O Laya roda na sua"
    "\n  máquina, em CPU, sem rede."
    "\n- Tokens de saída: nenhum deles gera texto. O número é o que cada API informa."
    "\n- O Laya zero-shot costuma ficar abaixo dos outros. A força dele é outra: roda local,"
    "\n  sem custo por chamada, e aceita fine-tune."
)
