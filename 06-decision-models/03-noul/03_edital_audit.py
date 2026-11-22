"""Aula 03 · Script 03: auditar um edital de concurso público com perguntas de sim ou não.

Um edital de concurso precisa trazer um conjunto de informações: cargos e vagas, remuneração,
inscrição, isenção da taxa, reserva de vagas, data e critério da prova, conteúdo programático,
recursos e validade. Cada item vira uma pergunta de sim ou não. As dez vão na mesma chamada,
e o modelo devolve a probabilidade de "sim" para cada uma.

O script audita dois editais fictícios: um completo e um com lacunas. No fim de cada um,
o código monta o parecer: o que está ausente e o que precisa de revisão humana.

Rode: python 06-decision-models/03-noul/03_edital_audit.py
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

# Duas faixas e um meio: abaixo de AUSENTE o item falta; acima de PRESENTE o item está lá;
# entre os dois, uma pessoa confere.
AUSENTE, PRESENTE = 0.30, 0.70

# No Windows, use 127.0.0.1 e não localhost (localhost tenta IPv6 primeiro e atrasa ~2 s).
LAYA_URL = os.environ.get("LAYA_BASE_URL", "http://127.0.0.1:8001")

# Cada item da auditoria: a pergunta e, quando a fronteira é discutível, o que conta como
# sim e o que conta como não. As perguntas são afirmativas: "sim" é sempre a presença do item.
AUDITORIA = {
    "cargos_e_vagas": {"pergunta": "O edital informa os cargos e o número de vagas de cada cargo?"},
    "remuneracao": {
        "pergunta": "O edital informa o valor da remuneração de cada cargo?",
        "sim": "traz o valor em reais da remuneração de cada cargo",
        "nao": "não traz valores, ou só remete a uma lei ou a um plano de cargos e salários",
    },
    "inscricao": {"pergunta": "O edital informa o período, a forma e o valor da taxa de inscrição?"},
    "isencao_da_taxa": {
        "pergunta": "O edital prevê isenção da taxa de inscrição para candidatos de baixa renda?"
    },
    "reserva_pcd": {"pergunta": "O edital reserva vagas para pessoas com deficiência?"},
    "data_da_prova": {
        "pergunta": "O edital informa a data da prova?",
        "sim": "traz o dia em que a prova será aplicada",
        "nao": "diz que a data será divulgada depois, ou não fala em data",
    },
    "criterio_de_aprovacao": {
        "pergunta": "O edital define a nota mínima ou o critério para o candidato ser aprovado?"
    },
    "conteudo_programatico": {
        "pergunta": "O edital traz o conteúdo programático das provas?",
        "sim": "lista os assuntos que serão cobrados",
        "nao": "só diz que o conteúdo será divulgado depois, ou não trata do assunto",
    },
    "recursos": {"pergunta": "O edital prevê prazo e forma para o candidato apresentar recurso?"},
    "validade": {"pergunta": "O edital informa o prazo de validade do concurso?"},
}

# O que uma pessoa responderia lendo cada edital. Serve para você conferir a tabela.
ESPERADO = {
    "edital_completo.txt": {item: "sim" for item in AUDITORIA},
    "edital_com_lacunas.txt": {
        "cargos_e_vagas": "sim", "remuneracao": "não", "inscricao": "sim", "isencao_da_taxa": "não",
        "reserva_pcd": "não", "data_da_prova": "não", "criterio_de_aprovacao": "sim",
        "conteudo_programatico": "não", "recursos": "não", "validade": "não",
    },
}  # fmt: skip


# --- Jev e Laya: `noul`, com `criteria` opcional de `true` e `false` -------------------------
def ask_typesafe(client: TypeSafeClient, edital: str) -> dict:
    perguntas = {}
    for nome, item in AUDITORIA.items():
        criteria = {"true": item["sim"], "false": item["nao"]} if "sim" in item else None
        perguntas[nome] = Noul(instructions=item["pergunta"], criteria=criteria)
    with client:
        start = time.perf_counter()
        response = client.system_one(state={"edital": edital}, questions=perguntas)
        latency_ms = (time.perf_counter() - start) * 1000
    return {
        "sim": {nome: response.nouls[nome].noul for nome in AUDITORIA},
        "tokens_in": response.usage.input_tokens or 0,
        "latency_ms": latency_ms,
    }


def ask_jev(edital: str) -> dict:
    return ask_typesafe(TypeSafeClient(), edital)


def ask_laya(edital: str) -> dict:
    # O SDK exige uma chave não vazia; o Laya local aceita qualquer uma.
    client = TypeSafeClient(base_url=LAYA_URL, api_key="laya-local", model="multilingual")
    return ask_typesafe(client, edital)


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
def ask_gemini(edital: str) -> dict:
    perguntas = {}
    for nome, item in AUDITORIA.items():
        perguntas[nome] = {"type": "noul", "instructions": item["pergunta"]}
        if "sim" in item:
            perguntas[nome]["criteria"] = {"true_description": item["sim"], "false_description": item["nao"]}
    data, latency_ms = post(
        "https://generativelanguage.googleapis.com/v1beta/decisions",
        {"x-goog-api-key": os.environ["GEMINI_API_KEY"]},
        {"model": "gemini-decision-1", "input": edital, "questions": perguntas},
    )
    return {
        "sim": {nome: data["answers"][nome]["noul"] for nome in AUDITORIA},
        "tokens_in": data["usage"]["total_input_tokens"],
        "latency_ms": latency_ms,
    }


# --- OpenAI Decisions API: `predicate`. Não há campo para descrever o sim e o não, -----------
# --- então a regra vai inteira no texto da pergunta. A resposta vem em `probability`. --------
def ask_openai(edital: str) -> dict:
    perguntas = []
    for nome, item in AUDITORIA.items():
        texto = item["pergunta"]
        if "sim" in item:
            texto += f" Responda sim quando o edital {item['sim']}. Responda não quando {item['nao']}."
        perguntas.append({"type": "predicate", "name": nome, "instructions": texto})
    data, latency_ms = post(
        "https://api.openai.com/v1/decisions",
        {"Authorization": f"Bearer {os.environ['OPENAI_API_KEY']}"},
        {"model": "gpt-6-luna", "input": edital, "questions": perguntas},
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
    edital = (DOCS / arquivo).read_text(encoding="utf-8")
    respostas = {}
    for nome, ask in ativos.items():
        try:
            respostas[nome] = ask(edital)
        except Exception as error:  # um provedor fora do ar não derruba a comparação
            print(f"[{nome} falhou em {arquivo}: {' '.join(str(error).split())[:140]}]")

    print(f"\nEdital: {arquivo}  ({len(edital)} caracteres)")
    print("Probabilidade de SIM para cada item da auditoria:")
    cabecalho = f"  {'item da auditoria':<23} {'esperado':<9}" + "".join(f"{nome:>9}" for nome in respostas)
    print(cabecalho)
    print("  " + "-" * (len(cabecalho) - 2))
    for item in AUDITORIA:
        linha = "".join(cell(r["sim"].get(item)) for r in respostas.values())
        print(f"  {item:<23} {esperado[item]:<9}{linha}")
    print("  " + "-" * (len(cabecalho) - 2))
    print(f"  {'tokens de entrada':<33}" + "".join(f"{r['tokens_in']:>9}" for r in respostas.values()))
    print(f"  {'latência (ms)':<33}" + "".join(f"{r['latency_ms']:>9.0f}" for r in respostas.values()))

    # O parecer é do código: ele lê as probabilidades e separa o que falta do que é dúvida.
    print("\n  Parecer do código, por modelo:")
    for nome, r in respostas.items():
        ausentes = [i for i in AUDITORIA if (r["sim"].get(i) or 0) < AUSENTE]
        revisar = [i for i in AUDITORIA if AUSENTE <= (r["sim"].get(i) or 0) <= PRESENTE]
        print(f"  {nome:<7} ausentes: {', '.join(ausentes) or 'nenhum'}")
        if revisar:
            print(f"  {'':<7} revisar:  {', '.join(revisar)}")

print(
    "\nO que observar:"
    "\n- Dez perguntas, uma chamada, um parecer. O modelo só diz a probabilidade de cada item"
    "\n  estar no edital; quem monta a lista de pendências é o código."
    "\n- O edital com lacunas tem três armadilhas: a remuneração 'seguirá o plano de cargos', a prova"
    "\n  será 'em data a ser divulgada' e o conteúdo 'será divulgado em edital complementar'. O assunto"
    "\n  aparece no texto, mas a informação não está lá. É a descrição do sim e do não que resolve."
    "\n- Compare o parecer de cada modelo com a coluna 'esperado'. Onde eles divergem é onde a"
    "\n  pergunta precisa ser reescrita ou o limiar ajustado."
    "\n- O Laya, sem ajuste nos seus dados, tende a responder 'sim' a quase tudo: ele aprovaria o"
    "\n  edital com lacunas. Repare também nos tokens e na latência dele."
    "\n- Auditoria é ação de alto risco. Use o parecer como triagem: uma pessoa confirma as pendências."
)
