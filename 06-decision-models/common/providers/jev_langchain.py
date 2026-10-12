"""Provider pelo LangChain (`langchain-typesafe`): o `TypeSafeClassifier` é um Runnable.

Vantagem sobre o SDK puro: entra em chains, `batch`, callbacks e traces do LangSmith
(com tokens), e aceita mensagens do LangChain dentro do estado.
"""

from __future__ import annotations

import os
import time

from langchain_typesafe import Choice, Noul, Score, TypeSafeClassifier

from common.decisions import DecisionResult, DecisionSpec, answers_from_systemone, to_wire_questions
from common.pricing import cost_usd
from common.providers.jev_sdk import JEV_BASE_URL, JEV_MODEL


QUESTION_TYPES = {"choice": Choice, "noul": Noul, "score": Score}


def to_langchain_questions(questions: list[DecisionSpec]) -> dict:
    """DecisionSpec -> objetos `Choice` / `Noul` / `Score` do langchain-typesafe."""
    return {name: QUESTION_TYPES[q["type"]].model_validate(q) for name, q in to_wire_questions(questions).items()}


def make_classifier(target: str = "jev-langchain") -> TypeSafeClassifier:
    """Cria o classificador já ligado ao modo atual (replay, live ou record).

    Em replay, o classificador é o de verdade: só o transporte HTTP é trocado por um que
    responde a partir das fixtures. Todo o resto do código do LangChain roda igual.
    """
    import httpx2

    from common.providers.replay import RecordingTransport, is_live, is_recording, replay_transport

    if target == "laya":
        from common.providers.jev_sdk import LAYA_BASE_URL, LAYA_MODEL

        base_url = os.environ.get("LAYA_BASE_URL") or LAYA_BASE_URL
        api_key = os.environ.get("LAYA_API_KEY") or "laya-local"
        model = os.environ.get("LAYA_MODEL") or LAYA_MODEL
    else:
        base_url = os.environ.get("TYPESAFE_BASE_URL") or JEV_BASE_URL
        api_key = os.environ.get("TYPESAFE_API_KEY") or None
        model = os.environ.get("JEV_MODEL") or JEV_MODEL

    if not is_live(target):
        transport = replay_transport(target)
        api_key = "replay"
    elif is_recording(target):
        transport = RecordingTransport(target, origin=f"langchain-typesafe -> {base_url}", provider=target)
    else:
        transport = None

    kwargs = {"model": model, "base_url": base_url}
    if api_key:
        kwargs["api_key"] = api_key
    if transport is not None:
        kwargs["client"] = httpx2.Client(transport=transport, timeout=30)
    return TypeSafeClassifier(**kwargs)


class JevLangChainClient:
    def __init__(self, classifier: TypeSafeClassifier | None = None, provider: str = "jev-langchain"):
        self.provider = provider
        self.classifier = classifier or make_classifier(provider)

    def decide(self, state: dict | str, questions: list[DecisionSpec]) -> DecisionResult:
        start = time.perf_counter()
        response = self.classifier.invoke({"state": state, "questions": to_langchain_questions(questions)})
        latency_ms = (time.perf_counter() - start) * 1000

        raw = response.model_dump(mode="json")
        tokens_in, tokens_out = response.usage.input_tokens, response.usage.output_tokens
        return DecisionResult(
            provider=self.provider,
            model=response.model,
            answers=answers_from_systemone(raw["answers"]),
            latency_ms=latency_ms,
            tokens_in=tokens_in,
            tokens_out=tokens_out,
            cost_usd=cost_usd(response.model, tokens_in, tokens_out),
            raw=raw,
        )
