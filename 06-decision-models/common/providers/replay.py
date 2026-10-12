"""Replay e gravação: o bloco inteiro roda sem chave de API (RF-03).

Três modos, escolhidos por `DECISION_PROVIDER`:

- `replay` (padrão): toda decisão sai de `fixtures/<alvo>/<chave>.json`. Nada vai para a rede.
- `live`: chama os providers de verdade (precisa de chave ou do Laya rodando).
- `record`: chama de verdade os alvos em `DECISION_RECORD_ONLY` e grava a resposta;
  os demais alvos continuam em replay. É o que `05_replay_record.py` usa.

A chave da fixture é o hash do estado + perguntas (ver `request_key`). A mesma gravação
serve ao `DecisionClient` e ao replay em nível HTTP usado pelos scripts de LangChain.
"""

from __future__ import annotations

import json
import os
import sys
import time
from collections.abc import Callable
from datetime import date
from pathlib import Path
from typing import Any

import httpx2

from common.decisions import (
    DecisionResult,
    DecisionSpec,
    request_key,
    to_wire_questions,
)

BLOCK_DIR = Path(__file__).resolve().parents[2]
FIXTURES_DIR = BLOCK_DIR / "fixtures"
MODES = ("replay", "live", "record")


class ReplayMissError(Exception):
    """Não existe gravação para esta requisição."""


def mode() -> str:
    value = (os.environ.get("DECISION_PROVIDER") or "replay").strip().lower()
    if value not in MODES:
        raise ValueError(f"DECISION_PROVIDER={value!r}; use um de {MODES}")
    return value


def record_only() -> set[str]:
    raw = os.environ.get("DECISION_RECORD_ONLY", "")
    return {t.strip() for t in raw.split(",") if t.strip()}


def is_live(target: str) -> bool:
    """Este alvo chama a API de verdade no modo atual?"""
    current = mode()
    if current == "live":
        return True
    if current == "record":
        only = record_only()
        return not only or target in only or fixture_dir_name(target) in only
    return False


def is_recording(target: str) -> bool:
    return mode() == "record" and is_live(target)


def force_record() -> bool:
    """Em record, regrava mesmo o que já existe (padrão: reaproveita e não paga de novo)."""
    return os.environ.get("DECISION_RECORD_FORCE") == "1"


def _existing(target: str, key: str) -> dict | None:
    path = fixture_path(target, key)
    if force_record() or not path.exists():
        return None
    fixture = json.loads(path.read_text(encoding="utf-8"))
    return None if fixture.get("synthetic") else fixture


def fixture_dir_name(target: str) -> str:
    """'jev' e 'jev-langchain' compartilham gravações: é o mesmo modelo por outra superfície."""
    if target in ("jev", "jev-langchain"):
        return "jev"
    return target.replace(":", "-").replace("/", "-")


def fixture_path(target: str, key: str) -> Path:
    return FIXTURES_DIR / fixture_dir_name(target) / f"{key}.json"


_warned_synthetic: set[str] = set()


def _warn_synthetic(target: str, origin: str) -> None:
    if target in _warned_synthetic:
        return
    _warned_synthetic.add(target)
    print(
        f"\n⚠️  [replay] As gravações de '{fixture_dir_name(target)}' são SINTÉTICAS ({origin}).\n"
        "   Os números deste provider ilustram o formato, não medem o modelo.\n"
        "   Grave as reais com: python 05-calibration-evaluation/05_replay_record.py\n",
        file=sys.stderr,
    )


def load_fixture(target: str, key: str) -> dict[str, Any]:
    path = fixture_path(target, key)
    if not path.exists():
        raise ReplayMissError(
            f"sem gravação de '{target}' para a chave {key} ({path.relative_to(BLOCK_DIR)}).\n"
            "Você mudou a pergunta ou o estado? Em replay, só o que foi gravado responde.\n"
            "Rode com DECISION_PROVIDER=live, ou grave com 05-calibration-evaluation/05_replay_record.py"
        )
    fixture = json.loads(path.read_text(encoding="utf-8"))
    if fixture.get("synthetic"):
        _warn_synthetic(target, fixture.get("origin", "sem origem"))
    return fixture


def write_fixture(target: str, key: str, request: dict, result: dict, origin: str) -> Path:
    path = fixture_path(target, key)
    path.parent.mkdir(parents=True, exist_ok=True)
    fixture = {
        "key": key,
        "target": target,
        "recorded_at": date.today().isoformat(),
        "synthetic": False,
        "origin": origin,
        "request": request,
        "result": result,
    }
    path.write_text(json.dumps(fixture, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path


# ---------------------------------------------------------------------------
# Nível DecisionClient
# ---------------------------------------------------------------------------


class ReplayClient:
    """Devolve o `DecisionResult` gravado, com a latência e os tokens originais."""

    def __init__(self, target: str, simulate_latency: bool | None = None):
        self.target = target
        self.provider = target
        if simulate_latency is None:
            simulate_latency = os.environ.get("REPLAY_SIMULATE_LATENCY", "0") == "1"
        self.simulate_latency = simulate_latency

    def decide(self, state: dict | str, questions: list[DecisionSpec]) -> DecisionResult:
        key = request_key(state, to_wire_questions(questions))
        fixture = load_fixture(self.target, key)
        result = DecisionResult.model_validate(fixture["result"])
        result.synthetic = bool(fixture.get("synthetic"))
        result.provider = self.target  # 'jev-langchain' reaproveita a gravação de 'jev'
        if self.simulate_latency:
            time.sleep(result.latency_ms / 1000)
        return result


class RecordingClient:
    """Chama o cliente real e grava a resposta como fixture."""

    def __init__(self, target: str, inner, origin: str):
        self.target = target
        self.provider = inner.provider
        self.inner = inner
        self.origin = origin

    def decide(self, state: dict | str, questions: list[DecisionSpec]) -> DecisionResult:
        wire = to_wire_questions(questions)
        key = request_key(state, wire)
        if existing := _existing(self.target, key):
            return DecisionResult.model_validate(existing["result"])
        result = self.inner.decide(state, questions)
        write_fixture(
            self.target,
            key,
            request={"state": state, "questions": wire},
            result=result.model_dump(mode="json"),
            origin=self.origin,
        )
        return result


# ---------------------------------------------------------------------------
# Nível HTTP: para o TypeSafeClassifier e os middlewares do langchain-typesafe
# ---------------------------------------------------------------------------


def _body_key(request: httpx2.Request) -> tuple[str, dict]:
    body = json.loads(request.content)
    return request_key(body["state"], body["questions"]), body


def replay_transport(target: str) -> httpx2.MockTransport:
    """Transporte HTTP que responde `/v1/systemone` a partir das fixtures."""

    def handler(request: httpx2.Request) -> httpx2.Response:
        key, _ = _body_key(request)
        fixture = load_fixture(target, key)
        return httpx2.Response(200, json=fixture["result"]["raw"])

    return httpx2.MockTransport(handler)


class RecordingTransport(httpx2.BaseTransport):
    """Encaminha para o servidor real e grava cada resposta de `/v1/systemone`."""

    def __init__(self, target: str, origin: str, provider: str):
        self.target = target
        self.origin = origin
        self.provider = provider
        self.inner = httpx2.HTTPTransport()

    def handle_request(self, request: httpx2.Request) -> httpx2.Response:
        from common.decisions import answers_from_systemone
        from common.pricing import cost_usd

        key, body = _body_key(request)
        if existing := _existing(self.target, key):
            return httpx2.Response(200, json=existing["result"]["raw"])
        start = time.perf_counter()
        response = self.inner.handle_request(request)
        response.read()
        latency_ms = (time.perf_counter() - start) * 1000
        if response.status_code == 200:
            raw = response.json()
            usage = raw.get("usage") or {}
            result = DecisionResult(
                provider=self.provider,
                model=raw["model"],
                answers=answers_from_systemone(raw["answers"]),
                latency_ms=latency_ms,
                tokens_in=usage.get("input_tokens"),
                tokens_out=usage.get("output_tokens"),
                cost_usd=cost_usd(raw["model"], usage.get("input_tokens"), usage.get("output_tokens")),
                raw=raw,
            )
            write_fixture(
                self.target,
                key,
                request={"state": body["state"], "questions": body["questions"]},
                result=result.model_dump(mode="json"),
                origin=self.origin,
            )
        return response


# ---------------------------------------------------------------------------
# Chamadas genéricas (geração de texto, function calling, judge LLM)
# ---------------------------------------------------------------------------


def cached_call(target: str, request: dict, fn: Callable[[], dict], origin: str) -> dict:
    """Grava/reproduz qualquer chamada que devolve JSON.

    Usado onde a chamada não é uma decisão tipada: a resposta gerada pelo LLM no projeto
    final, o function calling do módulo 02, o judge LLM do módulo 04.
    """
    key = request_key(request, {})
    if not is_live(target):
        return load_fixture(target, key)["result"]
    if is_recording(target) and (existing := _existing(target, key)):
        return existing["result"]
    result = fn()
    if is_recording(target):
        write_fixture(target, key, request=request, result=result, origin=origin)
    return result

