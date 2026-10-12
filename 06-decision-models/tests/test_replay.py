import json

import httpx2
import pytest

from common.decisions import Answer, DecisionResult, DecisionSpec, request_key, to_wire_questions
from common.providers import replay

SPEC = [DecisionSpec(name="urgente", type="noul", instructions="É urgente?")]


class FakeClient:
    provider = "laya"

    def decide(self, state, questions):
        return DecisionResult(
            provider="laya",
            model="laya-rl-agent",
            answers={"urgente": Answer(value=0.9)},
            latency_ms=42.0,
            tokens_in=10,
            tokens_out=0,
            cost_usd=0.0,
            raw={
                "model": "laya-rl-agent",
                "answers": {"urgente": {"type": "noul", "noul": 0.9}},
                "usage": {"input_tokens": 10, "output_tokens": 0},
            },
        )


@pytest.fixture
def tmp_fixtures(tmp_path, monkeypatch):
    monkeypatch.setattr(replay, "FIXTURES_DIR", tmp_path)
    monkeypatch.setattr(replay, "BLOCK_DIR", tmp_path)
    return tmp_path


def test_modo_padrao_e_replay(monkeypatch):
    monkeypatch.delenv("DECISION_PROVIDER", raising=False)
    assert replay.mode() == "replay"
    assert not replay.is_live("jev")


def test_modo_invalido_falha(monkeypatch):
    monkeypatch.setenv("DECISION_PROVIDER", "jev")
    with pytest.raises(ValueError):
        replay.mode()


def test_record_only_restringe_alvos(monkeypatch):
    monkeypatch.setenv("DECISION_PROVIDER", "record")
    monkeypatch.setenv("DECISION_RECORD_ONLY", "laya")
    assert replay.is_recording("laya")
    assert not replay.is_live("jev")


def test_grava_e_reproduz(tmp_fixtures):
    recorder = replay.RecordingClient("laya", FakeClient(), origin="teste")
    original = recorder.decide("texto", SPEC)
    replayed = replay.ReplayClient("laya").decide("texto", SPEC)
    assert replayed.answers == original.answers
    assert replayed.latency_ms == 42.0
    assert not replayed.synthetic


def test_miss_explica_o_que_fazer(tmp_fixtures):
    with pytest.raises(replay.ReplayMissError, match="05_replay_record"):
        replay.ReplayClient("laya").decide("outro texto", SPEC)


def test_transporte_http_reproduz_a_mesma_fixture(tmp_fixtures):
    replay.RecordingClient("laya", FakeClient(), origin="teste").decide("texto", SPEC)
    client = httpx2.Client(transport=replay.replay_transport("laya"))
    body = {"state": "texto", "model": "qualquer", "questions": to_wire_questions(SPEC)}
    response = client.post("http://x/v1/systemone", json=body)
    assert response.json()["answers"]["urgente"]["noul"] == 0.9


def test_fixture_sintetica_e_marcada(tmp_fixtures, capsys):
    key = request_key("texto", to_wire_questions(SPEC))
    path = replay.fixture_path("jev", key)
    path.parent.mkdir(parents=True)
    result = FakeClient().decide("texto", SPEC).model_dump(mode="json")
    path.write_text(json.dumps({"synthetic": True, "origin": "teste", "result": result}), encoding="utf-8")
    replay._warned_synthetic.clear()
    assert replay.ReplayClient("jev").decide("texto", SPEC).synthetic
    assert "SINTÉTICAS" in capsys.readouterr().err


def test_cached_call_grava_e_reproduz(tmp_fixtures, monkeypatch):
    calls = []

    def fn():
        calls.append(1)
        return {"texto": "olá"}

    monkeypatch.setenv("DECISION_PROVIDER", "record")
    assert replay.cached_call("geracao", {"p": 1}, fn, origin="teste") == {"texto": "olá"}
    monkeypatch.setenv("DECISION_PROVIDER", "replay")
    assert replay.cached_call("geracao", {"p": 1}, fn, origin="teste") == {"texto": "olá"}
    assert len(calls) == 1
