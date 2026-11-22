"""Aula 03 · Script 01: um checklist de contrato com perguntas de sim ou não, em quatro modelos.

O jurídico recebe um documento e precisa conferir uma lista antes de aprovar: tem cláusula de
sigilo? Define o foro? Está assinado? Cada item é uma pergunta de sim ou não. Todas vão na
mesma chamada, e o modelo devolve a probabilidade de "sim" para cada uma.

O script passa o mesmo checklist em dois documentos parecidos: um contrato e a proposta
comercial que veio antes dele. A proposta tem quase as mesmas condições, mas não é um contrato.

Rode: python 06-decision-models/03-noul/01_contract_checklist.py
Usa TYPESAFE_API_KEY, GEMINI_API_KEY e OPENAI_API_KEY. Um provedor sem chave é pulado.
O Laya não precisa de chave, mas precisa estar no ar (da raiz do repositório):
    docker compose --profile decision up -d laya
"""

import os
import time
from pathlib import Path

import httpx
from dotenv import load_dotenv
from typesafe_sdk import Noul, TypeSafeClient

load_dotenv()

DOCS = Path(__file__).parent / "docs"

# No Windows, use 127.0.0.1 e não localhost (localhost tenta IPv6 primeiro e atrasa ~2 s).
LAYA_URL = os.environ.get("LAYA_BASE_URL", "http://127.0.0.1:8001")

# Cada item do checklist: a pergunta e, quando a fronteira é discutível, o que conta como
# sim e o que conta como não. As perguntas são afirmativas: "sim" é sempre a presença do item.
CHECKLIST = {
    "sigilo": {"pergunta": "O documento tem cláusula de confidencialidade ou sigilo?"},
    "multa_por_atraso": {"pergunta": "O documento prevê multa ou juros por atraso no pagamento?"},
    "garantia": {"pergunta": "O documento prevê a correção de defeitos sem custo por um período?"},
    "rescisao_com_aviso": {
        "pergunta": "O documento permite que qualquer das partes encerre o acordo mediante aviso prévio?"
    },
    "foro": {"pergunta": "O documento define o foro ou a comarca para resolver disputas?"},
    "assinaturas": {"pergunta": "O documento tem campo de assinatura para as duas partes?"},
    "renovacao_automatica": {
        "pergunta": "O documento prevê renovação automática do prazo?",
        "sim": "o prazo se renova sozinho se nenhuma das partes se manifestar",
        "nao": "a prorrogação depende de novo acordo, termo aditivo ou nova assinatura",
    },
    "obrigacao_imediata": {
        "pergunta": "O documento já cria obrigação entre as partes?",
        "sim": "é um acordo firmado, que vale a partir da assinatura",
        "nao": "é uma oferta ou proposta que ainda depende da assinatura de um contrato",
    },
}

# O que uma pessoa responderia lendo cada documento. Serve para você conferir a tabela.
ESPERADO = {
    "contrato_prestacao_servicos.txt": {
        "sigilo": "sim", "multa_por_atraso": "sim", "garantia": "sim", "rescisao_com_aviso": "sim",
        "foro": "sim", "assinaturas": "sim", "renovacao_automatica": "não", "obrigacao_imediata": "sim",
    },
    "proposta_comercial.txt": {
        "sigilo": "sim", "multa_por_atraso": "não", "garantia": "sim", "rescisao_com_aviso": "não",
        "foro": "não", "assinaturas": "não", "renovacao_automatica": "não", "obrigacao_imediata": "não",
    },
}  # fmt: skip


# --- Jev e Laya: `noul`, com `criteria` opcional de `true` e `false` -------------------------
def ask_typesafe(client: TypeSafeClient, documento: str) -> dict:
    perguntas = {}
    for nome, item in CHECKLIST.items():
        criteria = {"true": item["sim"], "false": item["nao"]} if "sim" in item else None
        perguntas[nome] = Noul(instructions=item["pergunta"], criteria=criteria)
    with client:
        start = time.perf_counter()
        response = client.system_one(state={"documento": documento}, questions=perguntas)
        latency_ms = (time.perf_counter() - start) * 1000
    return {
        "sim": {nome: response.nouls[nome].noul for nome in CHECKLIST},
        "tokens_in": response.usage.input_tokens or 0,
        "latency_ms": latency_ms,
    }


def ask_jev(documento: str) -> dict:
    return ask_typesafe(TypeSafeClient(), documento)


def ask_laya(documento: str) -> dict:
    # O SDK exige uma chave não vazia; o Laya local aceita qualquer uma.
    client = TypeSafeClient(base_url=LAYA_URL, api_key="laya-local", model="multilingual")
    return ask_typesafe(client, documento)


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


# --- Gemini Decision 1: `noul`, com `true_description` e `false_description` -----------------
def ask_gemini(documento: str) -> dict:
    perguntas = {}
    for nome, item in CHECKLIST.items():
        perguntas[nome] = {"type": "noul", "instructions": item["pergunta"]}
        if "sim" in item:
            perguntas[nome]["criteria"] = {"true_description": item["sim"], "false_description": item["nao"]}
    data, latency_ms = post(
        "https://generativelanguage.googleapis.com/v1beta/decisions",
        {"x-goog-api-key": os.environ["GEMINI_API_KEY"]},
        {"model": "gemini-decision-1", "input": documento, "questions": perguntas},
    )
    return {
        "sim": {nome: data["answers"][nome]["noul"] for nome in CHECKLIST},
        "tokens_in": data["usage"]["total_input_tokens"],
        "latency_ms": latency_ms,
    }


# --- OpenAI Decisions API: `predicate`. Não há campo para descrever o sim e o não, -----------
# --- então a regra vai inteira no texto da pergunta. A resposta vem em `probability`. --------
def ask_openai(documento: str) -> dict:
    perguntas = []
    for nome, item in CHECKLIST.items():
        texto = item["pergunta"]
        if "sim" in item:
            texto += f" Responda sim quando {item['sim']}. Responda não quando {item['nao']}."
        perguntas.append({"type": "predicate", "name": nome, "instructions": texto})
    data, latency_ms = post(
        "https://api.openai.com/v1/decisions",
        {"Authorization": f"Bearer {os.environ['OPENAI_API_KEY']}"},
        {"model": "gpt-6-luna", "input": documento, "questions": perguntas},
    )
    # Uma resposta pode vir como "refusal", sem probabilidade.
    return {
        "sim": {a["name"]: a.get("probability") for a in data["answers"]},
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
        ask("aquecimento")  # a primeira chamada abre a conexão (e, no Laya, carrega o modelo)
        ativos[nome] = ask
    except Exception as error:
        print(f"[{nome} falhou no aquecimento: {' '.join(str(error).split())[:160]}]")


def cell(p: float | None) -> str:
    return f"{'recusou':>9}" if p is None else f"{p:>9.0%}"


for arquivo, esperado in ESPERADO.items():
    documento = (DOCS / arquivo).read_text(encoding="utf-8")
    respostas = {}
    for nome, ask in ativos.items():
        try:
            respostas[nome] = ask(documento)
        except Exception as error:  # um provedor fora do ar não derruba a comparação
            print(f"[{nome} falhou em {arquivo}: {' '.join(str(error).split())[:140]}]")

    print(f"\nDocumento: {arquivo}  ({len(documento)} caracteres)")
    print("Probabilidade de SIM para cada item do checklist:")
    cabecalho = f"  {'item do checklist':<22} {'esperado':<9}" + "".join(f"{nome:>9}" for nome in respostas)
    print(cabecalho)
    print("  " + "-" * (len(cabecalho) - 2))
    for item in CHECKLIST:
        linha = "".join(cell(r["sim"].get(item)) for r in respostas.values())
        print(f"  {item:<22} {esperado[item]:<9}{linha}")
    print("  " + "-" * (len(cabecalho) - 2))
    print(f"  {'tokens de entrada':<32}" + "".join(f"{r['tokens_in']:>9}" for r in respostas.values()))
    print(f"  {'latência (ms)':<32}" + "".join(f"{r['latency_ms']:>9.0f}" for r in respostas.values()))

print(
    "\nO que observar:"
    "\n- Oito perguntas, uma chamada. Cada pergunta é independente: várias podem ser 'sim' ao mesmo"
    "\n  tempo. É o que um Choice não faz."
    "\n- Compare as duas tabelas. A proposta tem sigilo e garantia, como o contrato, mas não tem foro,"
    "\n  assinaturas nem multa. O checklist separa os dois documentos item por item."
    "\n- 'renovacao_automatica' e 'obrigacao_imediata' são os itens discutíveis. Neles, a descrição do"
    "\n  que conta como sim e como não é o que define a resposta."
    "\n- Valores perto de 50% são dúvida. Não trate como sim nem como não: mande para uma pessoa."
    "\n- O Laya, sem ajuste nos seus dados, tende a responder 'sim' a quase tudo. Repare também nos"
    "\n  tokens e na latência dele: o documento é processado de novo a cada pergunta, enquanto os"
    "\n  modelos por API leem o documento uma vez só para as oito."
)
