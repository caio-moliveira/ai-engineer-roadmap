"""Fábrica de clientes: `get_client("jev" | "jev-langchain" | "laya" | "llm:<modelo>")`.

O modo vem de `DECISION_PROVIDER` (replay, live ou record; padrão: replay). O código dos
módulos nunca sabe se está em replay: ele pede um cliente e chama `decide`.
"""

from __future__ import annotations

import os

from common.decisions import DecisionClient
from common.providers.replay import RecordingClient, ReplayClient, is_live, is_recording, mode

# Baselines LLM. O GPT-5.6 Luna está no plano do bloco, mas só o Claude Haiku 4.5 tem
# gravações reais neste repositório; troque com DECISION_LLM quando gravar outro.
DEFAULT_LLM = "anthropic:claude-haiku-4-5-20251001"
LLM_CATALOG = {
    "GPT-5.6 Luna": "openai:gpt-5.6-luna",
    "Claude Haiku 4.5": "anthropic:claude-haiku-4-5-20251001",
}


def default_llm() -> str:
    return os.environ.get("DECISION_LLM") or DEFAULT_LLM


def default_target() -> str:
    return os.environ.get("DECISION_TARGET") or "jev"


def compare_targets() -> list[str]:
    """Alvos das comparações lado a lado: Jev, Laya e o LLM de baseline."""
    raw = os.environ.get("DECISION_TARGETS")
    if raw:
        return [t.strip() for t in raw.split(",") if t.strip()]
    return ["jev", "laya", f"llm:{default_llm()}"]


def _live_client(target: str) -> DecisionClient:
    if target == "jev":
        from common.providers.jev_sdk import JevSDKClient

        return JevSDKClient.jev()
    if target == "laya":
        from common.providers.jev_sdk import JevSDKClient

        return JevSDKClient.laya()
    if target == "jev-langchain":
        from common.providers.jev_langchain import JevLangChainClient

        return JevLangChainClient()
    if target.startswith("llm:"):
        from common.providers.llm import LLMClient

        return LLMClient(target.removeprefix("llm:"))
    raise ValueError(f"alvo desconhecido: {target!r}")


def _origin(target: str) -> str:
    if target == "laya":
        return f"laya-serve em {os.environ.get('LAYA_BASE_URL') or 'http://127.0.0.1:8001'}, modelo multilingual"
    if target in ("jev", "jev-langchain"):
        return "API TypeSafe (Jev)"
    return f"LangChain init_chat_model + with_structured_output ({target.removeprefix('llm:')})"


def get_client(target: str | None = None) -> DecisionClient:
    target = target or default_target()
    if target == "jev-langchain":
        # O cliente LangChain troca o transporte HTTP sozinho conforme o modo.
        from common.providers.jev_langchain import JevLangChainClient

        return JevLangChainClient()
    if not is_live(target):
        return ReplayClient(target)
    client = _live_client(target)
    if is_recording(target):
        return RecordingClient(target, client, origin=_origin(target))
    return client


__all__ = ["DEFAULT_LLM", "LLM_CATALOG", "compare_targets", "default_llm", "default_target", "get_client", "mode"]
