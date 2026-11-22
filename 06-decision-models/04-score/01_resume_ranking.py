"""Aula 04 · Script 01: ranquear currículos para uma vaga com Scores, em quatro modelos.

O RH recebeu seis currículos para uma vaga de engenharia de dados. Em vez de perguntar "o
candidato é bom?", o script faz três perguntas de "quanto", cada uma com a sua escala:
experiência com pipelines, aderência à stack da vaga e autonomia. As três vão na mesma chamada.

O modelo devolve um score por escala. O código normaliza os três, aplica os pesos e ordena os
candidatos pela nota final. No fim, um zoom mostra o que existe por trás de um score: a
probabilidade de cada nível.

Rode: python 06-decision-models/04-score/01_resume_ranking.py
Usa TYPESAFE_API_KEY, GEMINI_API_KEY e OPENAI_API_KEY. Um provedor sem chave é pulado.
O Laya não precisa de chave, mas precisa estar no ar (da raiz do repositório):
    docker compose --profile decision up -d laya
"""

import os
import time
from pathlib import Path

import httpx
from dotenv import load_dotenv
from typesafe_sdk import Score, TypeSafeClient

load_dotenv()

DOCS = Path(__file__).parent / "docs"

# No Windows, use 127.0.0.1 e não localhost (localhost tenta IPv6 primeiro e atrasa ~2 s).
LAYA_URL = os.environ.get("LAYA_BASE_URL", "http://127.0.0.1:8001")

# Cada escala: a pergunta, o peso na nota final e os níveis, do mais baixo para o mais alto.
# Cada nível é (rótulo, descrição). A descrição conta uma situação, não um grau ("bom", "ótimo").
ESCALAS = {
    "experiencia": {
        "pergunta": "Quanta experiência o candidato tem construindo pipelines de dados?",
        "peso": 0.5,
        "niveis": [
            ("nenhuma", "nunca trabalhou com dados"),
            ("ao redor", "trabalhou com dados em análise, BI ou backend, sem construir pipelines"),
            ("inicial", "construiu pipelines de dados em estágio, projetos pessoais ou com ajuda do time"),
            ("em produção", "construiu e manteve pipelines de dados em produção por alguns anos"),
        ],
    },
    "stack": {
        "pergunta": "Quanto das tecnologias pedidas na vaga aparece no currículo?",
        "peso": 0.3,
        "niveis": [
            ("nada", "não cita Python, SQL nem ferramentas de dados"),
            ("pouco", "cita SQL ou Python, mas não orquestração de pipelines"),
            ("boa parte", "cita Python, SQL e orquestração, ainda em nível de noções"),
            ("tudo", "cita Python, SQL, orquestração de pipelines e nuvem em uso profissional"),
        ],
    },
    "autonomia": {
        "pergunta": "Com quanta autonomia o candidato trabalha hoje?",
        "peso": 0.2,
        "niveis": [
            ("apoiado", "está em estágio ou depende do time para concluir as tarefas"),
            ("independente", "conduz o próprio trabalho sem supervisão"),
            ("referência", "lidera pessoas ou projetos, ou orienta colegas"),
        ],
    },
}


def join_input(partes: dict) -> str:
    """Gemini e OpenAI recebem a entrada como um texto só."""
    return "\n\n".join(f"{nome.upper()}:\n{texto}" for nome, texto in partes.items())


# --- Jev e Laya: `score`, com os níveis numa lista em `criteria` -----------------------------
def ask_typesafe(client: TypeSafeClient, partes: dict) -> dict:
    perguntas = {
        nome: Score(instructions=e["pergunta"], criteria=[f"{r}: {d}" for r, d in e["niveis"]])
        for nome, e in ESCALAS.items()
    }
    with client:
        start = time.perf_counter()
        response = client.system_one(state=partes, questions=perguntas)
        latency_ms = (time.perf_counter() - start) * 1000
    return {
        "score": {nome: response.scores[nome].score for nome in ESCALAS},
        "probs": {
            nome: [response.scores[nome].probabilities.get(i, 0.0) for i in range(len(e["niveis"]))]
            for nome, e in ESCALAS.items()
        },
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
        nome: {"type": "score", "instructions": e["pergunta"], "criteria": [f"{r}: {d}" for r, d in e["niveis"]]}
        for nome, e in ESCALAS.items()
    }
    data, latency_ms = post(
        "https://generativelanguage.googleapis.com/v1beta/decisions",
        {"x-goog-api-key": os.environ["GEMINI_API_KEY"]},
        {"model": "gemini-decision-1", "input": join_input(partes), "questions": perguntas},
    )
    answers = data["answers"]
    return {
        "score": {nome: answers[nome]["score"] for nome in ESCALAS},
        "probs": {
            nome: [answers[nome]["probabilities"].get(str(i), 0.0) for i in range(len(e["niveis"]))]
            for nome, e in ESCALAS.items()
        },
        "tokens_in": data["usage"]["total_input_tokens"],
        "latency_ms": latency_ms,
    }


# --- OpenAI Decisions API: `score`, com os níveis em `levels` (rótulo e descrição) -----------
def ask_openai(partes: dict) -> dict:
    perguntas = [
        {
            "type": "score",
            "name": nome,
            "instructions": e["pergunta"],
            "levels": [{"label": r, "description": d} for r, d in e["niveis"]],
        }
        for nome, e in ESCALAS.items()
    ]
    data, latency_ms = post(
        "https://api.openai.com/v1/decisions",
        {"Authorization": f"Bearer {os.environ['OPENAI_API_KEY']}"},
        {"model": "gpt-6-luna", "input": join_input(partes), "questions": perguntas},
    )
    answers = {a["name"]: a for a in data["answers"]}
    return {
        "score": {nome: answers[nome]["score"] for nome in ESCALAS},
        # A OpenAI devolve uma lista de {value, label, probability}; ordenamos pelo índice do nível.
        "probs": {
            nome: [p["probability"] for p in sorted(answers[nome]["probabilities"], key=lambda p: p["value"])]
            for nome in ESCALAS
        },
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

vaga = (DOCS / "vaga.txt").read_text(encoding="utf-8")
curriculos = {
    path.stem.removeprefix("curriculo_"): path.read_text(encoding="utf-8")
    for path in sorted(DOCS.glob("curriculo_*.txt"))
}


def final_grade(scores: dict) -> float:
    """O código combina as três escalas: normaliza cada score para 0 a 1 e aplica os pesos."""
    return sum(e["peso"] * scores[nome] / (len(e["niveis"]) - 1) for nome, e in ESCALAS.items())


# resultados[modelo][candidato] = resposta do modelo
resultados: dict[str, dict[str, dict]] = {}
for nome, (disponivel, como_resolver, ask) in PROVEDORES.items():
    if not disponivel():
        print(f"[pulando {nome}: {como_resolver}]")
        continue
    try:
        ask({"vaga": "aquecimento", "curriculo": "aquecimento"})  # abre a conexão
        resultados[nome] = {c: ask({"vaga": vaga, "curriculo": texto}) for c, texto in curriculos.items()}
    except Exception as error:  # um provedor fora do ar não derruba a comparação
        print(f"[{nome} falhou: {' '.join(str(error).split())[:160]}]")

# --- 1. O ranking de cada modelo -------------------------------------------------------------
maximos = {nome: len(e["niveis"]) - 1 for nome, e in ESCALAS.items()}
for modelo, respostas in resultados.items():
    tokens = sum(r["tokens_in"] for r in respostas.values()) / len(respostas)
    latencia = sum(r["latency_ms"] for r in respostas.values()) / len(respostas)
    print(f"\nModelo: {modelo}   (por currículo, em média: {tokens:.0f} tokens de entrada, {latencia:.0f} ms)")
    cabecalho = (
        f"  {'posição':<8} {'candidato':<14}"
        + "".join(f"{f'{nome} (0 a {maximos[nome]})':>22}" for nome in ESCALAS)
        + f"{'nota final (0 a 1)':>21}"
    )
    print(cabecalho)
    print("  " + "-" * (len(cabecalho) - 2))
    ordenados = sorted(respostas.items(), key=lambda kv: -final_grade(kv[1]["score"]))
    for posicao, (candidato, r) in enumerate(ordenados, start=1):
        colunas = "".join(f"{r['score'][nome]:>22.2f}" for nome in ESCALAS)
        print(f"  {posicao:<8} {candidato:<14}{colunas}{final_grade(r['score']):>21.2f}")

# --- 2. A posição de cada candidato em cada modelo -------------------------------------------
if resultados:
    print("\nPosição de cada candidato no ranking de cada modelo:")
    cabecalho = f"  {'candidato':<14}" + "".join(f"{modelo:>9}" for modelo in resultados)
    print(cabecalho)
    print("  " + "-" * (len(cabecalho) - 2))
    posicoes = {
        modelo: {c: i for i, (c, _) in enumerate(sorted(rs.items(), key=lambda kv: -final_grade(kv[1]["score"])), 1)}
        for modelo, rs in resultados.items()
    }
    for candidato in curriculos:
        print(f"  {candidato:<14}" + "".join(f"{posicoes[modelo][candidato]:>8}º" for modelo in resultados))

# --- 3. Zoom: o que existe por trás de um score ----------------------------------------------
CANDIDATO, ESCALA = "bruno_costa", "autonomia"
if resultados:
    rotulos = [r for r, _ in ESCALAS[ESCALA]["niveis"]]
    print(f"\nZoom: a escala '{ESCALA}' para {CANDIDATO}. Probabilidade de cada nível:")
    cabecalho = (
        f"  {'modelo':<8}"
        + "".join(f"{f'{i} {rotulo}':>15}" for i, rotulo in enumerate(rotulos))
        + f"{'score':>9}{'nível mais provável':>22}"
    )
    print(cabecalho)
    print("  " + "-" * (len(cabecalho) - 2))
    for modelo, respostas in resultados.items():
        r = respostas[CANDIDATO]
        probs = r["probs"][ESCALA]
        mais_provavel = max(range(len(probs)), key=lambda i: probs[i])
        colunas = "".join(f"{p:>15.0%}" for p in probs)
        print(f"  {modelo:<8}{colunas}{r['score'][ESCALA]:>9.2f}{f'{mais_provavel} {rotulos[mais_provavel]}':>22}")

print(
    "\nO que observar:"
    "\n- O modelo não diz quem é o melhor candidato. Ele dá três scores por currículo; a nota final"
    "\n  e os pesos são regra do código. Mude os pesos e o ranking muda, sem chamar o modelo de novo."
    "\n- As escalas têm tamanhos diferentes (0 a 3 e 0 a 2). Por isso o código divide cada score"
    "\n  pelo nível máximo antes de somar."
    "\n- O score é uma média: fica entre dois níveis quando o modelo está dividido. No zoom, veja a"
    "\n  probabilidade de cada nível por trás do número."
    "\n- Para ordenar, use o score. Para agir sobre um nível ('só chamar quem está em produção'),"
    "\n  use o nível mais provável e confira a distribuição."
    "\n- Compare o ranking entre os modelos: onde eles trocam posições é onde a escala precisa de"
    "\n  níveis mais bem descritos."
)
