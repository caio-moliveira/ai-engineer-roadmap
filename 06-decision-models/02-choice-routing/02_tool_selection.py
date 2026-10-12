"""Módulo 02 · Script 02: escolher a tool com um Choice em vez de function calling.

Pergunta-chave: quantas vezes o seu agente lê 10 descrições de tool só para escolher uma?

O catálogo de tools vira o `criteria` de um Choice (common/specs.py: TOOL). Comparamos com
o caminho clássico: o LLM recebe as tools via `bind_tools` e decide qual chamar.
Golden set: 80 perguntas do agente de vendas do workshop-jev (inclui 20 adversariais).

Rode: python 02-choice-routing/02_tool_selection.py
"""

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.tools import StructuredTool

from common import golden, metrics
from common.evaluation import print_table, run_targets, summarize
from common.pricing import cost_usd
from common.providers import compare_targets, default_llm
from common.providers.llm import model_kwargs
from common.providers.replay import ReplayMissError, cached_call
from common.specs import NO_TOOL, TOOL, TOOLS

perguntas = golden.load("sales")
print(f"{len(perguntas)} perguntas de vendas; {len(TOOLS)} tools + '{NO_TOOL}'")

# --- 1. Choice: o catálogo vira criteria -------------------------------------------------
runs_by_target = run_targets(compare_targets(), perguntas, [TOOL])
rows = [summarize(TOOL, runs) for runs in runs_by_target.values()]

# --- 2. Function calling: o LLM lê as tools e escolhe qual chamar ------------------------
FC_SYSTEM = (
    "Você é o assistente de dados de vendas da empresa Mercado Jornada. Chame a única tool que responde "
    "a pergunta. Se nenhuma tool tiver o dado, não chame nenhuma."
)


def _noop() -> str:
    return "ok"


def function_calling(model: str, pergunta: str) -> dict:
    """Uma rodada de function calling. Devolve a tool escolhida, tokens e latência."""

    def call() -> dict:
        tools = [StructuredTool.from_function(_noop, name=name, description=desc) for name, desc in TOOLS.items()]
        llm = init_chat_model(model, **model_kwargs(model)).bind_tools(tools)
        start = time.perf_counter()
        message = llm.invoke([SystemMessage(FC_SYSTEM), HumanMessage(pergunta)])
        latency_ms = (time.perf_counter() - start) * 1000
        usage = message.usage_metadata or {}
        return {
            "tool": message.tool_calls[0]["name"] if message.tool_calls else NO_TOOL,
            "latency_ms": latency_ms,
            "tokens_in": usage.get("input_tokens", 0),
            "tokens_out": usage.get("output_tokens", 0),
        }

    request = {"tipo": "function_calling", "modelo": model, "system": FC_SYSTEM, "tools": TOOLS, "pergunta": pergunta}
    return cached_call(f"fc:{model}", request, call, origin=f"bind_tools ({model})")


llm = default_llm()
try:
    fc = [function_calling(llm, p.state["pergunta"]) for p in perguntas]
except ReplayMissError as error:
    fc = None
    print(f"\n⚠️  sem gravação de function calling para {llm}: {str(error).splitlines()[0]}")

if fc:
    truth = [p.labels["tool"] for p in perguntas]
    preds = [x["tool"] for x in fc]
    model_id = llm.split(":", 1)[-1]
    costs = [cost_usd(model_id, x["tokens_in"], x["tokens_out"]) for x in fc]
    rows.append(
        {
            "provider": f"function calling ({model_id})",
            "n": len(fc),
            "acurácia": metrics.accuracy(truth, preds),
            "f1_macro": metrics.f1_macro(truth, preds),
            "brier": None,
            "ece": None,
            "p50_ms": metrics.p50([x["latency_ms"] for x in fc]),
            "p95_ms": metrics.p95([x["latency_ms"] for x in fc]),
            "custo_1k_usd": sum(costs) / len(costs) * 1000,
            "tokens_in_médio": sum(x["tokens_in"] for x in fc) / len(fc),
            "falha_formato": 0,
        }
    )

print_table(rows, "Escolha de tool: Choice x function calling")

adversariais = [p for p in perguntas if "adversarial" in p.tags]
print(f"\nNas {len(adversariais)} perguntas adversariais (injeção, dado sensível, fora de escopo), o rótulo é '{NO_TOOL}'.")
print("Escolher tool não é o lugar de barrar ataque: isso é o guardrail do módulo 03, ANTES da triagem.")
print(
    "\nO que comparar além da acurácia:"
    "\n- tokens_in_médio: todo caminho com LLM relê as descrições das tools em toda chamada. O modelo de"
    "\n  decisão também as lê, mas cobra por token de entrada uma fração do preço e não gera saída."
    "\n- Com o Choice, o código recebe uma distribuição e decide o que fazer com a confiança;"
    "\n  com function calling, o LLM já escolheu e você só vê a escolha."
    "\n- Acurácia zero-shot baixa (como a do Laya aqui) não é o fim da conversa: é o caso de uso"
    "\n  do fine-tune do módulo 07, com o próprio catálogo de tools como dado de treino."
)
