"""Baseline "LLM decidindo": structured output a partir do mesmo `DecisionSpec`.

O LLM não devolve distribuição. Pedimos uma `confidence` autorrelatada, de 0 a 1, para
poder medir calibração lado a lado com Jev e Laya (módulo 05). Spoiler: autorrelato não é
probabilidade.
"""

from __future__ import annotations

import json
import time

from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import BaseModel, Field, create_model

from common.decisions import Answer, DecisionResult, DecisionSpec, check_in_schema
from common.pricing import cost_usd

SYSTEM_PROMPT = (
    "Você toma decisões sobre o estado recebido. Responda cada pergunta só com base nele, "
    "usando exatamente os valores permitidos, e informe sua confiança de 0 a 1 em cada resposta."
)

# `choice` fica como str livre de propósito: é o que permite medir quando o LLM inventa
# uma opção que não existe (values_in_schema=False).
VALUE_TYPES = {"choice": str, "score": int, "noul": float}


def model_kwargs(model: str) -> dict:
    """Decisão simples: sem raciocínio estendido e sem amostragem criativa."""
    if model.startswith("openai:"):
        return {"reasoning_effort": "none"}
    return {"temperature": 0}


class LLMClient:
    def __init__(self, model: str, chat_model=None):
        self.model = model  # "provedor:modelo", ex. "anthropic:claude-haiku-4-5-20251001"
        self.model_id = model.split(":", 1)[-1]
        self.provider = f"llm:{model}"
        self.chat_model = chat_model or init_chat_model(model, **model_kwargs(model))

    def decide(self, state: dict | str, questions: list[DecisionSpec]) -> DecisionResult:
        structured = self.chat_model.with_structured_output(build_schema(questions), include_raw=True)

        start = time.perf_counter()
        output = structured.invoke(build_messages(state, questions))
        latency_ms = (time.perf_counter() - start) * 1000

        raw = output["raw"]
        usage = raw.usage_metadata or {}
        tokens_in, tokens_out = usage.get("input_tokens", 0), usage.get("output_tokens", 0)
        parsed = output["parsed"]
        answers = {}
        if parsed is not None:
            for name, field in parsed.model_dump().items():
                answers[name] = Answer(value=field["value"], confidence=field["confidence"])
        return DecisionResult(
            provider=self.provider,
            model=self.model_id,
            answers=answers,
            latency_ms=latency_ms,
            tokens_in=tokens_in,
            tokens_out=tokens_out,
            cost_usd=cost_usd(self.model_id, tokens_in, tokens_out),
            parse_ok=parsed is not None,
            values_in_schema=parsed is not None and check_in_schema(questions, answers),
            raw={
                "content": raw.content if isinstance(raw.content, str) else json.dumps(raw.content, ensure_ascii=False),
                "parsing_error": str(output["parsing_error"]) if output["parsing_error"] else None,
            },
        )


def build_schema(questions: list[DecisionSpec]) -> type[BaseModel]:
    fields = {}
    for q in questions:
        answer = create_model(
            f"Resposta_{q.name}",
            value=(VALUE_TYPES[q.type], Field(description=describe_value(q))),
            confidence=(float, Field(description="Sua confiança na resposta, de 0 a 1.")),
        )
        fields[q.name] = (answer, Field(description=q.instructions))
    return create_model("Respostas", **fields)


def build_messages(state: dict | str, questions: list[DecisionSpec]):
    state_text = state if isinstance(state, str) else json.dumps(state, ensure_ascii=False, indent=2)
    perguntas = "\n\n".join(f"{q.name} ({q.type}): {q.instructions}\n{describe_value(q)}" for q in questions)
    return [
        SystemMessage(SYSTEM_PROMPT),
        HumanMessage(f"Estado:\n{state_text}\n\nPerguntas:\n\n{perguntas}"),
    ]


def describe_value(q: DecisionSpec) -> str:
    if q.type == "choice":
        options = "\n".join(f"- {label}: {text or ''}" for label, text in q.criteria.items())
        return f"Responda com uma das opções:\n{options}"
    if q.type == "score":
        levels = "\n".join(f"- {i}: {text}" for i, text in enumerate(q.criteria))
        return f"Responda com o número do nível:\n{levels}"
    criteria = q.criteria or {}
    return (
        "Responda com a probabilidade, de 0 a 1, de a afirmação ser verdadeira.\n"
        f"- verdadeiro: {criteria.get('true', 'sim')}\n- falso: {criteria.get('false', 'não')}"
    )
