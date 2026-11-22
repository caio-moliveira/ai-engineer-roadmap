"""Aula 04 · Script 02: um juiz de respostas com Scores, em quatro modelos.

Um assistente de RAG respondeu a uma pergunta sobre um edital de concurso. Antes de a resposta
ir para o usuário, um modelo de decisão dá duas notas a ela, cada uma numa escala:
- fidelidade: o que a resposta afirma está no trecho do edital?
- completude: a resposta cobre tudo o que foi perguntado?

As duas notas saem na mesma chamada. O código decide com elas: aprova a resposta, manda o
assistente refazer ou barra por informação inventada.

O script julga cinco respostas escritas à mão, uma para cada tipo de falha comum.

Rode: python 06-decision-models/04-score/02_answer_judge.py
Usa TYPESAFE_API_KEY, GEMINI_API_KEY e OPENAI_API_KEY. Um provedor sem chave é pulado.
O Laya não precisa de chave, mas precisa estar no ar (da raiz do repositório):
    docker compose --profile decision up -d laya
"""

import os
import time

import httpx
from dotenv import load_dotenv
from typesafe_sdk import Score, TypeSafeClient

load_dotenv()

# No Windows, use 127.0.0.1 e não localhost (localhost tenta IPv6 primeiro e atrasa ~2 s).
LAYA_URL = os.environ.get("LAYA_BASE_URL", "http://127.0.0.1:8001")

MINIMO = 1.5  # nota mínima, numa escala de 0 a 2, para a resposta passar em cada critério

PERGUNTA = "Qual é o valor da taxa de inscrição e até quando posso pagar?"

CONTEXTO = (
    "3.2. O valor da taxa de inscrição é de R$ 60,00 para o cargo de nível médio e de R$ 95,00 "
    "para os cargos de nível superior.\n"
    "3.3. O pagamento deverá ser feito por boleto bancário até o dia 1º de junho de 2026."
)

# letra -> (o que esta resposta tem de particular, a resposta do assistente)
RESPOSTAS = {
    "A": (
        "correta e completa",
        "A taxa é de R$ 60,00 para o cargo de nível médio e de R$ 95,00 para os de nível superior. "
        "O pagamento é por boleto bancário, até 1º de junho de 2026.",
    ),
    "B": (
        "correta, mas não diz o prazo",
        "A taxa é de R$ 60,00 para o cargo de nível médio e de R$ 95,00 para os de nível superior.",
    ),
    "C": (
        "valor inventado",
        "A taxa é de R$ 80,00 para todos os cargos, e o pagamento pode ser feito até 1º de junho de 2026.",
    ),
    "D": (
        "completa, com um detalhe inventado",
        "A taxa é de R$ 60,00 (nível médio) ou R$ 95,00 (nível superior), paga por boleto até 1º de "
        "junho de 2026. Quem pagar por Pix tem 10% de desconto.",
    ),
    "E": (
        "não responde",
        "Recomendo consultar o edital no site da prefeitura para ver os valores e os prazos atualizados.",
    ),
}

# Cada critério: a pergunta e os níveis, do mais baixo para o mais alto. Nível = (rótulo, descrição).
CRITERIOS = {
    "fidelidade": {
        "pergunta": "Quanto do que a resposta afirma está no contexto?",
        "niveis": [
            ("contradiz", "a resposta afirma algo que contradiz o contexto"),
            ("acrescenta", "a resposta acerta o que cita do contexto, mas acrescenta informação que não está nele"),
            ("fiel", "tudo o que a resposta afirma está no contexto"),
        ],
    },
    "completude": {
        "pergunta": "Quanto da pergunta a resposta cobre?",
        "niveis": [
            ("nada", "a resposta não traz nenhuma das informações pedidas"),
            ("parte", "a resposta traz só uma parte das informações pedidas"),
            ("tudo", "a resposta traz todas as informações pedidas"),
        ],
    },
}


def join_input(partes: dict) -> str:
    """Gemini e OpenAI recebem a entrada como um texto só."""
    return "\n\n".join(f"{nome.upper()}:\n{texto}" for nome, texto in partes.items())


# --- Jev e Laya: `score`, com os níveis numa lista em `criteria` -----------------------------
def ask_typesafe(client: TypeSafeClient, partes: dict) -> dict:
    perguntas = {
        nome: Score(instructions=c["pergunta"], criteria=[f"{r}: {d}" for r, d in c["niveis"]])
        for nome, c in CRITERIOS.items()
    }
    with client:
        start = time.perf_counter()
        response = client.system_one(state=partes, questions=perguntas)
        latency_ms = (time.perf_counter() - start) * 1000
    return {
        "score": {nome: response.scores[nome].score for nome in CRITERIOS},
        "tokens_in": response.usage.input_tokens or 0,
        "latency_ms": latency_ms,
    }


def ask_jev(partes: dict) -> dict:
    return ask_typesafe(TypeSafeClient(), partes)


def ask_laya(partes: dict) -> dict:
    # O SDK exige uma chave não vazia; o Laya local aceita qualquer uma.
    client = TypeSafeClient(base_url=LAYA_URL, api_key="laya-local", model="multilingual")
    return ask_typesafe(client, partes)


def laya_no_ar() -> bool:
    try:
        httpx.get(f"{LAYA_URL}/health", timeout=3).raise_for_status()
        return True
    except httpx.HTTPError:
        return False


def post(url: str, headers: dict, body: dict) -> tuple[dict, float]:
    """POST com medição de tempo. Em erro, mostra a mensagem que a API devolveu."""
    start = time.perf_counter()
    response = httpx.post(url, headers=headers, json=body, timeout=60)
    latency_ms = (time.perf_counter() - start) * 1000
    if response.status_code >= 400:
        raise RuntimeError(f"HTTP {response.status_code}: {response.text}")
    return response.json(), latency_ms


# --- Gemini Decision 1: `score`, também com a lista em `criteria` ----------------------------
def ask_gemini(partes: dict) -> dict:
    perguntas = {
        nome: {"type": "score", "instructions": c["pergunta"], "criteria": [f"{r}: {d}" for r, d in c["niveis"]]}
        for nome, c in CRITERIOS.items()
    }
    data, latency_ms = post(
        "https://generativelanguage.googleapis.com/v1beta/decisions",
        {"x-goog-api-key": os.environ["GEMINI_API_KEY"]},
        {"model": "gemini-decision-1", "input": join_input(partes), "questions": perguntas},
    )
    return {
        "score": {nome: data["answers"][nome]["score"] for nome in CRITERIOS},
        "tokens_in": data["usage"]["total_input_tokens"],
        "latency_ms": latency_ms,
    }


# --- OpenAI Decisions API: `score`, com os níveis em `levels` (rótulo e descrição) -----------
def ask_openai(partes: dict) -> dict:
    perguntas = [
        {
            "type": "score",
            "name": nome,
            "instructions": c["pergunta"],
            "levels": [{"label": r, "description": d} for r, d in c["niveis"]],
        }
        for nome, c in CRITERIOS.items()
    ]
    data, latency_ms = post(
        "https://api.openai.com/v1/decisions",
        {"Authorization": f"Bearer {os.environ['OPENAI_API_KEY']}"},
        {"model": "gpt-6-luna", "input": join_input(partes), "questions": perguntas},
    )
    return {
        "score": {a["name"]: a["score"] for a in data["answers"]},
        "tokens_in": data["usage"]["input_tokens"],
        "latency_ms": latency_ms,
    }


# nome -> (está disponível?, o que fazer se não estiver, função que pergunta)
PROVEDORES = {
    "Jev": (lambda: bool(os.environ.get("TYPESAFE_API_KEY")), "defina TYPESAFE_API_KEY no .env", ask_jev),
    "Laya": (laya_no_ar, "suba com: docker compose --profile decision up -d laya", ask_laya),
    "Gemini": (lambda: bool(os.environ.get("GEMINI_API_KEY")), "defina GEMINI_API_KEY no .env", ask_gemini),
    "OpenAI": (lambda: bool(os.environ.get("OPENAI_API_KEY")), "defina OPENAI_API_KEY no .env", ask_openai),
}

ativos = {}
for nome, (disponivel, como_resolver, ask) in PROVEDORES.items():
    if not disponivel():
        print(f"[pulando {nome}: {como_resolver}]")
        continue
    try:
        ask({"pergunta": "aquecimento", "contexto": "aquecimento", "resposta": "aquecimento"})
        ativos[nome] = ask
    except Exception as error:
        print(f"[{nome} falhou no aquecimento: {' '.join(str(error).split())[:160]}]")


def verdict(score: dict) -> str:
    """O código decide com as duas notas. Informação inventada pesa mais que resposta incompleta."""
    if score["fidelidade"] < MINIMO:
        return "BARRA: informação que não está no contexto"
    if score["completude"] < MINIMO:
        return "REFAZ: resposta incompleta"
    return "aprova"


print(f"\nPergunta: {PERGUNTA}")
print(f"Contexto (trecho do edital):\n  {CONTEXTO.replace(chr(10), chr(10) + '  ')}")
print(f"\nNotas de 0 a 2. Para passar, a resposta precisa de pelo menos {MINIMO} em cada critério.")

for letra, (particularidade, resposta) in RESPOSTAS.items():
    print(f"\nResposta {letra} ({particularidade}): {resposta}")
    cabecalho = f"  {'modelo':<8} {'fidelidade':>11} {'completude':>11} {'latência':>10}   decisão do código"
    print(cabecalho)
    print("  " + "-" * (len(cabecalho) + 26))
    for nome, ask in ativos.items():
        try:
            r = ask({"pergunta": PERGUNTA, "contexto": CONTEXTO, "resposta": resposta})
        except Exception as error:  # um provedor fora do ar não derruba a comparação
            print(f"  {nome:<8} erro: {' '.join(str(error).split())[:110]}")
            continue
        print(
            f"  {nome:<8} {r['score']['fidelidade']:>11.2f} {r['score']['completude']:>11.2f}"
            f" {r['latency_ms']:>7.0f} ms   {verdict(r['score'])}"
        )

print(
    "\nO que observar:"
    "\n- Dois critérios, duas escalas. 'A resposta é boa?' numa nota só misturaria as duas coisas:"
    "\n  a resposta B é fiel e incompleta; a resposta D é completa e inventa um desconto."
    "\n- O modelo dá as notas; quem aprova, manda refazer ou barra é o código, com a regra que você"
    "\n  escreve. Aqui, informação inventada barra antes de a completude ser olhada."
    "\n- A resposta E falha nos dois critérios: não traz nenhuma informação pedida (completude perto"
    "\n  de 0) e cita um site que não está no contexto (fidelidade perto de 1). O motivo que aparece"
    "\n  depende da ordem das regras no código."
    "\n- A resposta D é o caso difícil: quase tudo está certo, e uma frase é inventada. É o tipo de"
    "\n  erro que um juiz precisa pegar."
    "\n- Um juiz também erra. Use as notas para triagem e meça o juiz com exemplos seus antes de"
    "\n  deixá-lo barrar respostas sozinho."
)
