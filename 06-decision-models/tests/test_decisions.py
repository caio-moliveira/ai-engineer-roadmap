import pytest

from common.decisions import (
    Answer,
    DecisionSpec,
    answers_from_systemone,
    check_in_schema,
    request_key,
    to_wire_questions,
)
from common.providers.jev_langchain import to_langchain_questions

CHOICE = DecisionSpec(name="fila", type="choice", instructions="Qual fila?", criteria={"a": "x", "b": None})
NOUL = DecisionSpec(name="urgente", type="noul", instructions="É urgente?")
NOUL_CRIT = DecisionSpec(name="spam", type="noul", instructions="É spam?", criteria={"true": "sim", "false": "não"})
SCORE = DecisionSpec(name="nivel", type="score", instructions="Qual nível?", criteria=["baixo", "alto"])


def test_criteria_validada():
    with pytest.raises(ValueError):
        DecisionSpec(name="x", type="choice", instructions="?", criteria=["a"])
    with pytest.raises(ValueError):
        DecisionSpec(name="x", type="score", instructions="?", criteria={"a": 1})


def test_nomes_repetidos_falham():
    with pytest.raises(ValueError):
        to_wire_questions([NOUL, NOUL])


def test_mesma_chave_pelo_sdk_e_pelo_langchain():
    """O replay HTTP (LangChain) e o replay de decisão precisam achar a mesma fixture."""
    state = {"ticket": "oi"}
    specs = [CHOICE, NOUL, NOUL_CRIT, SCORE]
    wire = to_wire_questions(specs)
    lc = {k: v.model_dump(mode="json", exclude_none=True) for k, v in to_langchain_questions(specs).items()}
    assert request_key(state, wire) == request_key(state, lc)


def test_chave_muda_quando_a_pergunta_muda():
    other = CHOICE.model_copy(update={"instructions": "Qual fila deve atender?"})
    assert request_key("s", to_wire_questions([CHOICE])) != request_key("s", to_wire_questions([other]))


def test_normaliza_resposta_systemone():
    raw = {
        "fila": {"type": "choice", "choice": "a", "confidence": 0.9, "probabilities": {"a": 0.9, "b": 0.1}},
        "urgente": {"type": "noul", "noul": 0.8},
        "nivel": {"type": "score", "score": 0.7, "confidence": 0.6, "probabilities": {"0": 0.3, "1": 0.7}, "legend": {}},
        "futuro": {"type": "tipo-novo"},
    }
    answers = answers_from_systemone(raw)
    assert answers["fila"].value == "a"
    assert answers["urgente"].value == 0.8
    assert answers["nivel"].value == 1 and answers["nivel"].expected == 0.7
    assert "futuro" not in answers
    assert check_in_schema([CHOICE, NOUL, SCORE], answers)


def test_valor_fora_do_schema():
    assert not check_in_schema([CHOICE], {"fila": Answer(value="c")})
    assert not check_in_schema([SCORE], {"nivel": Answer(value=5)})
