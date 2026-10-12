"""Provider pelo SDK oficial (`typesafe-sdk`). Atende o Jev e o Laya.

O Laya local (`laya-serve`) fala o mesmo `POST /v1/systemone` do Jev. Por isso o mesmo
cliente serve os dois: muda a `base_url`, a chave e o nome do modelo, e mais nada.
"""

from __future__ import annotations

import os
import time

from typesafe_sdk import TypeSafeClient

from common.decisions import (
    DecisionResult,
    DecisionSpec,
    answers_from_systemone,
    to_wire_questions,
)
from common.pricing import cost_usd

JEV_BASE_URL = "https://api.typesafe.ai"
JEV_MODEL = "jev-1.13.0"
LAYA_BASE_URL = "http://127.0.0.1:8001"
LAYA_MODEL = "multilingual"  # checkpoint mmBERT; o checkpoint em inglês não serve para pt-BR


class JevSDKClient:
    def __init__(
        self,
        *,
        provider: str = "jev",
        base_url: str | None = None,
        api_key: str | None = None,
        model: str | None = None,
        timeout: float = 30.0,
    ):
        self.provider = provider
        self.model = model
        # api_key=None faz o SDK ler TYPESAFE_API_KEY do ambiente.
        self._client = TypeSafeClient(api_key=api_key, base_url=base_url, model=model, timeout=timeout)

    @classmethod
    def jev(cls) -> JevSDKClient:
        return cls(
            provider="jev",
            base_url=os.environ.get("TYPESAFE_BASE_URL") or JEV_BASE_URL,
            model=os.environ.get("JEV_MODEL") or JEV_MODEL,
        )

    @classmethod
    def laya(cls) -> JevSDKClient:
        # O laya-serve só exige chave se LAYA_API_KEY estiver definida no servidor;
        # o SDK exige uma chave não vazia, então mandamos um valor qualquer.
        return cls(
            provider="laya",
            base_url=os.environ.get("LAYA_BASE_URL") or LAYA_BASE_URL,
            api_key=os.environ.get("LAYA_API_KEY") or "laya-local",
            model=os.environ.get("LAYA_MODEL") or LAYA_MODEL,
        )

    def decide(self, state: dict | str, questions: list[DecisionSpec]) -> DecisionResult:
        wire = to_wire_questions(questions)

        start = time.perf_counter()
        response = self._client.system_one(state=state, questions=wire)
        latency_ms = (time.perf_counter() - start) * 1000

        raw = response.raw_http_response.json()
        tokens_in = response.usage.input_tokens
        tokens_out = response.usage.output_tokens
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


def make_typesafe_client(target: str = "jev") -> TypeSafeClient:
    """`TypeSafeClient` do SDK já ligado ao modo atual, para scripts que usam o SDK direto.

    Em replay, o SDK roda de verdade (validação das perguntas, parse da resposta);
    só o transporte HTTP responde a partir das fixtures.
    """
    import httpx2

    from common.providers.replay import RecordingTransport, is_live, is_recording, replay_transport

    if target == "laya":
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
        transport = RecordingTransport(target, origin=f"typesafe-sdk -> {base_url}", provider=target)
    else:
        return TypeSafeClient(api_key=api_key, base_url=base_url, model=model)
    return TypeSafeClient(
        api_key=api_key, base_url=base_url, model=model, http_client=httpx2.Client(transport=transport, timeout=30)
    )
