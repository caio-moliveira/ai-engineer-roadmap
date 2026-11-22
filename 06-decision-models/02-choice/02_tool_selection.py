"""Aula 02 · Script 02: escolher a tool do agente com um Choice, em quatro modelos de decisão.

No function calling, o LLM lê a descrição de todas as tools e gera a chamada. Aqui, o catálogo
de tools de um agente de e-commerce vira as opções de um Choice: o modelo de decisão escolhe a
tool, e o código a executa. A opção "nenhuma" cobre pedidos que nenhuma tool atende.

Para cada pedido, o script mostra a tool que cada modelo escolheu e executa a do primeiro
modelo disponível, se a probabilidade passar do limiar.

Rode: python 06-decision-models/02-choice/02_tool_selection.py
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

LIMIAR = 0.70  # probabilidade mínima da tool escolhida para o código executá-la

# No Windows, use 127.0.0.1 e não localhost (localhost tenta IPv6 primeiro e atrasa ~2 s).
LAYA_URL = os.environ.get("LAYA_BASE_URL", "http://127.0.0.1:8001")


# As tools do agente. Aqui devolvem dados fixos; num sistema real, consultariam o banco.
def status_do_pedido() -> str:
    return "Pedido 4821: pago, em separação no centro de distribuição"


def rastrear_entrega() -> str:
    return "Pedido 4821: saiu para entrega em 03/11, previsão 07/11"


def abrir_devolucao() -> str:
    return "Devolução aberta: etiqueta de postagem enviada por e-mail"


def segunda_via_nota_fiscal() -> str:
    return "Nota fiscal do pedido 4821 reenviada por e-mail"


def consultar_estoque() -> str:
    return "Fone Bluetooth: 312 unidades no CD de Campinas"


def consultar_preco() -> str:
    return "Fone Bluetooth: R$ 189,90 à vista"


def calcular_frete() -> str:
    return "Frete para o CEP informado: R$ 18,40, entrega em 4 dias úteis"


def vendas_por_regiao() -> str:
    return "Sudeste R$ 4,2 mi | Sul R$ 1,9 mi | Nordeste R$ 1,1 mi"


def produtos_mais_vendidos() -> str:
    return "1. Fone Bluetooth  2. Carregador 65W  3. Smartwatch"


def falar_com_atendente() -> str:
    return "Conversa transferida para um atendente humano"


# nome da tool -> (função, descrição). A descrição é o que o modelo lê para escolher.
TOOLS = {
    "status_do_pedido": (status_do_pedido, "situação de um pedido: pago, em separação, faturado ou cancelado"),
    "rastrear_entrega": (rastrear_entrega, "onde está a encomenda de um pedido já enviado e a previsão de chegada"),
    "abrir_devolucao": (abrir_devolucao, "iniciar a devolução ou a troca de um produto já recebido, com reembolso"),
    "segunda_via_nota_fiscal": (segunda_via_nota_fiscal, "reenviar a nota fiscal de um pedido"),
    "consultar_estoque": (consultar_estoque, "quantidade disponível de um produto"),
    "consultar_preco": (consultar_preco, "preço atual de um produto"),
    "calcular_frete": (calcular_frete, "valor e prazo de entrega para um CEP"),
    "vendas_por_regiao": (vendas_por_regiao, "faturamento total agrupado por região do país"),
    "produtos_mais_vendidos": (produtos_mais_vendidos, "ranking dos produtos com mais unidades vendidas"),
    "falar_com_atendente": (falar_com_atendente, "o usuário pede uma pessoa ou faz uma reclamação grave"),
}

PERGUNTA = "Qual tool atende o pedido do usuário?"
OPCOES = {nome: descricao for nome, (_, descricao) in TOOLS.items()} | {
    "nenhuma": "nenhuma das tools tem o dado pedido, ou o pedido não é sobre a loja"
}

PEDIDOS = [
    "Meu pedido 4821 já saiu para entrega?",
    "Ainda tem fone bluetooth disponível?",
    "Qual região faturou mais este ano?",
    "Preciso da nota fiscal do pedido 4821 de novo.",
    "Meu pedido não chegou e eu quero meu dinheiro de volta.",
    "Quanto custa o fone bluetooth e quanto fica o frete para o CEP 39400-000?",
    "Isso é um absurdo, quero falar com alguém agora.",
    "Me passa o CPF dos clientes que mais compraram.",
    "Qual a previsão do tempo para amanhã?",
]


# --- Jev e Laya: o mesmo SDK e o mesmo código, só muda a base_url ----------------------------
def ask_typesafe(client: TypeSafeClient, pedido: str) -> dict:
    with client:
        start = time.perf_counter()
        response = client.system_one(
            state={"pedido": pedido},
            questions={"tool": Choice(instructions=PERGUNTA, criteria=OPCOES)},
        )
        latency_ms = (time.perf_counter() - start) * 1000
    answer = response.choices["tool"]
    return {
        "tool": answer.choice,
        "probabilidades": dict(answer.probabilities),
        "tokens_in": response.usage.input_tokens or 0,
        "latency_ms": latency_ms,
    }


def ask_jev(pedido: str) -> dict:
    return ask_typesafe(TypeSafeClient(), pedido)


def ask_laya(pedido: str) -> dict:
    # O SDK exige uma chave não vazia; o Laya local aceita qualquer uma.
    client = TypeSafeClient(base_url=LAYA_URL, api_key="laya-local", model="multilingual")
    return ask_typesafe(client, pedido)


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


# --- Gemini Decision 1: `input` no lugar de `state`; as opções vão em `criteria` -------------
def ask_gemini(pedido: str) -> dict:
    data, latency_ms = post(
        "https://generativelanguage.googleapis.com/v1beta/decisions",
        {"x-goog-api-key": os.environ["GEMINI_API_KEY"]},
        {
            "model": "gemini-decision-1",
            "input": pedido,
            "questions": {"tool": {"type": "choice", "instructions": PERGUNTA, "criteria": OPCOES}},
        },
    )
    answer = data["answers"]["tool"]
    return {
        "tool": answer["choice"],
        "probabilidades": answer["probabilities"],
        "tokens_in": data["usage"]["total_input_tokens"],
        "latency_ms": latency_ms,
    }


# --- OpenAI Decisions API: perguntas em lista, opções em `choices` ---------------------------
def ask_openai(pedido: str) -> dict:
    data, latency_ms = post(
        "https://api.openai.com/v1/decisions",
        {"Authorization": f"Bearer {os.environ['OPENAI_API_KEY']}"},
        {
            "model": "gpt-6-luna",
            "input": pedido,
            "questions": [
                {
                    "type": "choice",
                    "name": "tool",
                    "instructions": PERGUNTA,
                    "choices": [{"value": nome, "description": d} for nome, d in OPCOES.items()],
                }
            ],
        },
    )
    answer = data["answers"][0]
    probabilidades = {p["value"]: p["probability"] for p in answer["probabilities"]}
    return {
        "tool": answer["choice"],
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

latencias: dict[str, list[float]] = {nome: [] for nome in ativos}
tokens: dict[str, list[int]] = {nome: [] for nome in ativos}
todos_concordaram = apis_concordaram = 0

# Cada linha mostra as três tools mais prováveis para aquele modelo, com a porcentagem de cada uma.
CABECALHO = f"  {'modelo':<18}  {'1ª opção':<31} {'2ª opção':<31} {'3ª opção':<31} {'latência':>9}"
SEPARADOR = "  " + "-" * (len(CABECALHO) - 2)


def top3(probabilidades: dict) -> str:
    melhores = sorted(probabilidades.items(), key=lambda kv: -kv[1])[:3]
    return " ".join(f"{tool:<24}{p:>6.1%} " for tool, p in melhores)


for numero, pedido in enumerate(PEDIDOS, start=1):
    print(f"\nPedido {numero}: {pedido}")
    print(CABECALHO)
    print(SEPARADOR)
    respostas = {}
    for nome, ask in ativos.items():
        try:
            r = respostas[nome] = ask(pedido)
        except Exception as error:  # um provedor fora do ar não derruba a comparação
            print(f"  {nome:<18}  erro: {' '.join(str(error).split())[:110]}")
            continue
        latencias[nome].append(r["latency_ms"])
        tokens[nome].append(r["tokens_in"])
        print(f"  {nome:<18}  {top3(r['probabilidades'])}{r['latency_ms']:>6.0f} ms")

    if not respostas:
        continue
    if len({r["tool"] for r in respostas.values()}) == 1:
        todos_concordaram += 1
    if len({r["tool"] for nome, r in respostas.items() if nome != "Laya (local)"}) == 1:
        apis_concordaram += 1

    # Quem decide é o primeiro modelo disponível. O código só executa acima do limiar.
    decisor, r = next(iter(respostas.items()))
    probabilidade = r["probabilidades"][r["tool"]]
    if r["tool"] == "nenhuma":
        print(f"  Decisão ({decisor}): sem tool. O agente responde que não tem esse dado.")
    elif probabilidade < LIMIAR:
        print(
            f"  Decisão ({decisor}): {probabilidade:.0%} está abaixo do limiar de {LIMIAR:.0%}."
            " O agente pede para o usuário reformular."
        )
    else:
        funcao, _ = TOOLS[r["tool"]]
        print(f"  Decisão ({decisor}): executa {r['tool']}. Resultado: {funcao()}")

if ativos:
    print("\n\nRESUMO")
    print(f"  Mesma tool nos modelos por API: {apis_concordaram} de {len(PEDIDOS)} pedidos.")
    print(f"  Mesma tool em todos, com o Laya: {todos_concordaram} de {len(PEDIDOS)} pedidos.")
    cabecalho = f"  {'modelo':<18} {'tokens de entrada (média)':>26} {'latência (média)':>18}"
    print(f"\n{cabecalho}")
    print("  " + "-" * (len(cabecalho) - 2))
    for nome in ativos:
        if latencias[nome]:
            n = len(latencias[nome])
            print(f"  {nome:<18} {sum(tokens[nome]) / n:>26.0f} {sum(latencias[nome]) / n:>15.0f} ms")

print(
    "\nO que observar:"
    "\n- Quem executa a tool é o seu código, a partir de uma escolha com probabilidade. O modelo"
    "\n  não gera a chamada: não há argumento inventado nem nome de tool que não existe."
    "\n- Pedidos claros: os modelos por API concordam, com probabilidade alta. O Laya, sem ajuste"
    "\n  nos seus dados, se perde com onze opções e erra com probabilidade alta: probabilidade alta"
    "\n  só vale alguma coisa depois de medida nos seus exemplos."
    "\n- 'Já saiu para entrega?' divide os modelos entre status_do_pedido e rastrear_entrega: as"
    "\n  duas descrições cobrem o mesmo caso. É a fronteira entre opções que precisa ser reescrita."
    "\n- 'Não chegou e quero meu dinheiro de volta' fica entre rastrear e devolver, e 'preço e frete'"
    "\n  pede duas tools. O Choice devolve uma só: a dúvida aparece na probabilidade."
    "\n- Os argumentos (o número do pedido, o CEP), quando precisar, vêm de outra etapa: extração com"
    "\n  LLM ou com código. O Choice resolve só a escolha."
    "\n- O pedido de CPF não deveria chegar até aqui. Barrar dado sensível é trabalho de um"
    "\n  guardrail antes da escolha de tool, com Nouls (Aula 3)."
)
