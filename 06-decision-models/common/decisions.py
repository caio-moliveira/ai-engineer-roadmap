"""Contratos do bloco: a pergunta tipada, a resposta normalizada e o cliente de decisão.

Regra de ouro: o mesmo `DecisionSpec` alimenta todos os providers (Jev, Laya, LLM, replay).
Não existe prompt por modelo. O provider traduz a spec para o formato dele e devolve um
`DecisionResult` igual para todos.
"""

from __future__ import annotations

import hashlib
import json
from typing import Any, Literal, Protocol

from pydantic import BaseModel, Field, model_validator

QuestionType = Literal["choice", "score", "noul"]


class DecisionSpec(BaseModel):
    """Uma pergunta tipada.

    - choice: `criteria` é um dict {rótulo: descrição}.
    - score: `criteria` é uma lista ordenada de níveis, do 0 em diante.
    - noul: `criteria` é opcional, {"true": descrição, "false": descrição}.
    """

    name: str
    type: QuestionType
    instructions: str
    criteria: dict | list | None = None

    @model_validator(mode="after")
    def _check_criteria(self) -> DecisionSpec:
        if self.type == "choice" and not (isinstance(self.criteria, dict) and self.criteria):
            raise ValueError(f"choice '{self.name}' precisa de criteria como dict não vazio")
        if self.type == "score" and not (isinstance(self.criteria, list) and self.criteria):
            raise ValueError(f"score '{self.name}' precisa de criteria como lista não vazia")
        if self.type == "noul" and self.criteria is not None and not isinstance(self.criteria, dict):
            raise ValueError(f"noul '{self.name}' aceita criteria só como dict true/false")
        return self

    def to_wire(self) -> dict[str, Any]:
        """Formato do `POST /v1/systemone` (Jev e Laya falam o mesmo esquema)."""
        wire: dict[str, Any] = {"type": self.type, "instructions": self.instructions}
        if self.criteria is not None:
            wire["criteria"] = self.criteria
        return wire


class Answer(BaseModel):
    """Resposta de uma pergunta, igual para todo provider.

    - choice: `value` é o rótulo escolhido.
    - score: `value` é o nível mais provável (int); `expected` é a média ponderada.
    - noul: `value` é a probabilidade de a afirmação ser verdadeira (0 a 1).
    """

    value: str | int | float
    confidence: float | None = None  # Jev/Laya: do modelo; LLM: autorrelatada
    probabilities: dict[str, float] | None = None  # LLM não tem distribuição
    expected: float | None = None  # só score


class DecisionResult(BaseModel):
    provider: str  # "jev" | "jev-langchain" | "laya" | "llm:<modelo>"
    model: str
    answers: dict[str, Answer]
    latency_ms: float
    tokens_in: int | None = None
    tokens_out: int | None = None
    cost_usd: float | None = None
    parse_ok: bool = True  # só o LLM pode falhar no parse
    values_in_schema: bool = True  # o LLM pode inventar uma opção
    synthetic: bool = False  # True quando veio de fixture sintética (ver fixtures/README.md)
    raw: dict[str, Any] = Field(default_factory=dict, repr=False)


class DecisionClient(Protocol):
    provider: str

    def decide(self, state: dict | str, questions: list[DecisionSpec]) -> DecisionResult: ...


# ---------------------------------------------------------------------------
# Utilitários compartilhados pelos providers
# ---------------------------------------------------------------------------


def to_wire_questions(questions: list[DecisionSpec]) -> dict[str, dict[str, Any]]:
    names = [q.name for q in questions]
    if len(names) != len(set(names)):
        raise ValueError(f"nomes de pergunta repetidos: {names}")
    return {q.name: q.to_wire() for q in questions}


def canonical_json(obj: Any) -> str:
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def request_key(state: Any, wire_questions: dict[str, Any]) -> str:
    """Chave de uma requisição: hash do estado + perguntas no formato de fio.

    É a chave das fixtures de replay. Mudou uma vírgula na instrução, mudou a chave:
    a gravação antiga não vale para a pergunta nova.
    """
    payload = canonical_json({"state": state, "questions": wire_questions})
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:20]


def answers_from_systemone(raw_answers: dict[str, Any]) -> dict[str, Answer]:
    """Normaliza o JSON de `/v1/systemone` (Jev ou Laya) para `Answer`."""
    answers: dict[str, Answer] = {}
    for name, a in raw_answers.items():
        kind = a.get("type")
        if kind == "choice":
            answers[name] = Answer(
                value=a["choice"],
                confidence=a.get("confidence"),
                probabilities={str(k): float(v) for k, v in a["probabilities"].items()},
            )
        elif kind == "score":
            probs = {str(k): float(v) for k, v in a["probabilities"].items()}
            level = int(max(probs, key=probs.get))
            answers[name] = Answer(
                value=level,
                confidence=a.get("confidence"),
                probabilities=probs,
                expected=float(a["score"]),
            )
        elif kind == "noul":
            p = float(a["noul"])
            answers[name] = Answer(
                value=p,
                confidence=a.get("confidence"),
                probabilities={"true": p, "false": 1 - p},
            )
        # tipos novos que o bloco não conhece são ignorados, como o SDK faz
    return answers


def check_in_schema(questions: list[DecisionSpec], answers: dict[str, Answer]) -> bool:
    """A resposta usa só valores permitidos pela spec?"""
    for q in questions:
        if q.name not in answers:
            return False
        value = answers[q.name].value
        if q.type == "choice" and value not in q.criteria:
            return False
        if q.type == "score" and (not isinstance(value, int) or value not in range(len(q.criteria))):
            return False
        if q.type == "noul" and not (isinstance(value, int | float) and 0 <= value <= 1):
            return False
    return True


def prob_of(answer: Answer, label: Any) -> float | None:
    """Probabilidade que o provider deu ao rótulo `label` (None se não houver distribuição)."""
    if answer.probabilities is None:
        return None
    return answer.probabilities.get(str(label).lower() if isinstance(label, bool) else str(label))
