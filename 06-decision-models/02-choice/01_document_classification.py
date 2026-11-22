"""Aula 02 · Script 01: classificar documentos com um Choice, em quatro modelos de decisão.

Uma esteira de entrada recebe documentos e precisa saber o tipo de cada um antes de mandar
para o fluxo certo. Um Choice responde "que tipo de documento é este?" com a probabilidade
de cada tipo.

Parte 1: seis documentos, só com o começo de cada um.
Parte 2: o mesmo relatório em três tamanhos. É onde aparecem os limites de entrada de
cada modelo e quanto custa mandar o documento inteiro.

Rode: python 06-decision-models/02-choice/01_document_classification.py
Usa TYPESAFE_API_KEY, GEMINI_API_KEY e OPENAI_API_KEY. Um provedor sem chave é pulado.
O Laya não precisa de chave, mas precisa estar no ar (da raiz do repositório):
    docker compose --profile decision up -d laya
"""

import os
import time
from pathlib import Path

import httpx
from dotenv import load_dotenv
from pypdf import PdfReader
from typesafe_sdk import Choice, TypeSafeClient

load_dotenv()

DOCS = Path(__file__).parent / "docs"
INICIO = 3000  # na Parte 1, mandamos só os primeiros caracteres de cada documento

PERGUNTA = "Que tipo de documento é este?"
TIPOS = {
    "contrato": "acordo assinado entre partes, com cláusulas, obrigações, prazo e foro",
    "nota_fiscal": "documento fiscal de venda ou serviço, com valores, impostos e dados do emissor",
    "curriculo": "histórico profissional e formação de uma pessoa",
    "ata_de_reuniao": "registro do que foi discutido e decidido numa reunião, com participantes",
    "relatorio_tecnico": "texto longo que explica um assunto técnico ou científico",
    "outro": "qualquer documento que não seja de um dos tipos acima",
}

# Preço por 1 milhão de tokens de entrada, em dólares (novembro de 2026). O Laya roda local.
PRECO = {"Jev": 0.042, "Laya (local)": 0.0, "Gemini Decision 1": 0.10, "OpenAI Decisions": 0.10}

# No Windows, use 127.0.0.1 e não localhost (localhost tenta IPv6 primeiro e atrasa ~2 s).
LAYA_URL = os.environ.get("LAYA_BASE_URL", "http://127.0.0.1:8001")


def read_document(path: Path) -> list[str]:
    """Devolve o texto do documento, uma página por item."""
    if path.suffix == ".pdf":
        return [page.extract_text() or "" for page in PdfReader(path).pages]
    return [path.read_text(encoding="utf-8")]


# --- Jev e Laya: o mesmo SDK e o mesmo código, só muda a base_url ----------------------------
def ask_typesafe(client: TypeSafeClient, texto: str) -> dict:
    with client:
        start = time.perf_counter()
        response = client.system_one(
            state={"documento": texto},
            questions={"tipo": Choice(instructions=PERGUNTA, criteria=TIPOS)},
        )
        latency_ms = (time.perf_counter() - start) * 1000
    answer = response.choices["tipo"]
    return {
        "tipo": answer.choice,
        "probabilidades": dict(answer.probabilities),
        "tokens_in": response.usage.input_tokens or 0,
        "latency_ms": latency_ms,
    }


def ask_jev(texto: str) -> dict:
    return ask_typesafe(TypeSafeClient(), texto)


def ask_laya(texto: str) -> dict:
    # O SDK exige uma chave não vazia; o Laya local aceita qualquer uma.
    client = TypeSafeClient(base_url=LAYA_URL, api_key="laya-local", model="multilingual")
    return ask_typesafe(client, texto)


def laya_no_ar() -> bool:
    try:
        httpx.get(f"{LAYA_URL}/health", timeout=3).raise_for_status()
        return True
    except httpx.HTTPError:
        return False


def post(url: str, headers: dict, body: dict) -> tuple[dict, float]:
    """POST com medição de tempo. Em erro, mostra a mensagem que a API devolveu."""
    start = time.perf_counter()
    response = httpx.post(url, headers=headers, json=body, timeout=120)
    latency_ms = (time.perf_counter() - start) * 1000
    if response.status_code >= 400:
        raise RuntimeError(f"HTTP {response.status_code}: {response.text}")
    return response.json(), latency_ms


# --- Gemini Decision 1: `input` no lugar de `state`; as opções vão em `criteria` -------------
def ask_gemini(texto: str) -> dict:
    data, latency_ms = post(
        "https://generativelanguage.googleapis.com/v1beta/decisions",
        {"x-goog-api-key": os.environ["GEMINI_API_KEY"]},
        {
            "model": "gemini-decision-1",
            "input": texto,
            "questions": {"tipo": {"type": "choice", "instructions": PERGUNTA, "criteria": TIPOS}},
        },
    )
    answer = data["answers"]["tipo"]
    return {
        "tipo": answer["choice"],
        "probabilidades": answer["probabilities"],
        "tokens_in": data["usage"]["total_input_tokens"],
        "latency_ms": latency_ms,
    }


# --- OpenAI Decisions API: perguntas em lista, opções em `choices` ---------------------------
def ask_openai(texto: str) -> dict:
    data, latency_ms = post(
        "https://api.openai.com/v1/decisions",
        {"Authorization": f"Bearer {os.environ['OPENAI_API_KEY']}"},
        {
            "model": "gpt-6-luna",
            "input": texto,
            "questions": [
                {
                    "type": "choice",
                    "name": "tipo",
                    "instructions": PERGUNTA,
                    "choices": [{"value": nome, "description": d} for nome, d in TIPOS.items()],
                }
            ],
        },
    )
    answer = data["answers"][0]
    probabilidades = {p["value"]: p["probability"] for p in answer["probabilities"]}
    return {
        "tipo": answer["choice"],
        "probabilidades": probabilidades,
        "tokens_in": data["usage"]["input_tokens"],
        "latency_ms": latency_ms,
    }


# nome -> (está disponível?, o que fazer se não estiver, função que pergunta)
PROVEDORES = {
    "Jev": (lambda: bool(os.environ.get("TYPESAFE_API_KEY")), "defina TYPESAFE_API_KEY no .env", ask_jev),
    "Laya (local)": (laya_no_ar, "suba com: docker compose --profile decision up -d laya", ask_laya),
    "Gemini Decision 1": (lambda: bool(os.environ.get("GEMINI_API_KEY")), "defina GEMINI_API_KEY no .env", ask_gemini),
    "OpenAI Decisions": (lambda: bool(os.environ.get("OPENAI_API_KEY")), "defina OPENAI_API_KEY no .env", ask_openai),
}

ativos = {}
for nome, (disponivel, como_resolver, ask) in PROVEDORES.items():
    if not disponivel():
        print(f"[pulando {nome}: {como_resolver}]")
        continue
    try:
        ask("aquecimento")  # a primeira chamada abre a conexão (e, no Laya, carrega o modelo)
        ativos[nome] = ask
    except Exception as error:
        print(f"[{nome} falhou no aquecimento: {str(error)[:160]}]")


def try_ask(ask, texto: str) -> dict | str:
    """Devolve a resposta ou, se o provedor recusar a entrada, a mensagem de erro."""
    try:
        return ask(texto)
    except Exception as error:  # limite de tokens, limite de taxa, provedor fora do ar
        return " ".join(str(error).split())


# Uma coluna por tipo de documento, com a porcentagem que o modelo deu a cada um.
COLUNAS_TIPOS = " ".join(f"{tipo:>{max(len(tipo), 6)}}" for tipo in TIPOS)


def percentages(probabilidades: dict) -> str:
    return " ".join(f"{probabilidades.get(tipo, 0):>{max(len(tipo), 6)}.1%}" for tipo in TIPOS)


# --- Parte 1: seis documentos, só o começo de cada um ----------------------------------------
print(f"\nPARTE 1: classificar seis documentos pelos primeiros {INICIO} caracteres")
for path in sorted(DOCS.iterdir()):
    paginas = read_document(path)
    texto = "\n".join(paginas)
    print(f"\nDocumento: {path.name}  ({len(paginas)} página(s), {len(texto)} caracteres)")
    cabecalho = f"  {'modelo':<18} {'escolha':<18} {COLUNAS_TIPOS} {'tokens entrada':>15} {'latência':>10}"
    print(cabecalho)
    print("  " + "-" * (len(cabecalho) - 2))
    for nome, ask in ativos.items():
        r = try_ask(ask, texto[:INICIO])
        if isinstance(r, str):
            print(f"  {nome:<18} erro: {r[:110]}")
        else:
            print(
                f"  {nome:<18} {r['tipo']:<18} {percentages(r['probabilidades'])} {r['tokens_in']:>15}"
                f" {r['latency_ms']:>7.0f} ms"
            )

# --- Parte 2: o mesmo relatório em três tamanhos ---------------------------------------------
paginas = read_document(DOCS / "relatorio_mudancas_climaticas.pdf")
TAMANHOS = {
    "1 página": "\n".join(paginas[:1]),
    "10 páginas": "\n".join(paginas[:10]),
    f"{len(paginas)} páginas (inteiro)": "\n".join(paginas),
}

print("\n\nPARTE 2: o mesmo relatório em três tamanhos")
for nome, ask in ativos.items():
    print(f"\nModelo: {nome}")
    cabecalho = (
        f"  {'tamanho enviado':<22} {'escolha':<18} {COLUNAS_TIPOS} {'tokens entrada':>15} {'latência':>10}"
        f" {'custo (US$)':>12}"
    )
    print(cabecalho)
    print("  " + "-" * (len(cabecalho) - 2))
    for tamanho, texto in TAMANHOS.items():
        r = try_ask(ask, texto)
        if isinstance(r, str):
            print(f"  {tamanho:<22} erro: {r[:130]}")
        else:
            # custo desta chamada: tokens de entrada x preço por token (a saída é gratuita)
            custo = r["tokens_in"] * PRECO[nome] / 1_000_000
            print(
                f"  {tamanho:<22} {r['tipo']:<18} {percentages(r['probabilidades'])} {r['tokens_in']:>15}"
                f" {r['latency_ms']:>7.0f} ms {custo:>12.6f}"
            )

print(
    "\nO que observar:"
    "\n- Parte 1: nos documentos típicos, Jev, Gemini e OpenAI concordam com probabilidade alta."
    "\n  Compare com o Laya, que roda sem ajuste nos seus dados. A proposta comercial não tem tipo"
    "\n  próprio e se parece com um contrato: veja para onde cada modelo a manda."
    "\n- Parte 2: nos modelos por API, a resposta é a mesma com 1 página ou com o documento inteiro."
    "\n  O que muda é a conta: os tokens de entrada, e com eles o custo da chamada, crescem com o texto."
    "\n- Cada modelo tem um limite de entrada diferente. Os três por API leem o relatório inteiro."
    "\n  O Laya lê só o começo do texto (repare que os tokens param em 1024) e recusa o relatório inteiro."
    "\n- Para classificar, quase nunca é preciso mandar tudo: o começo do documento costuma bastar."
)
