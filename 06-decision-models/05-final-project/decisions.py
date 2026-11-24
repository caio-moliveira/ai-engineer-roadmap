"""Chamadas ao modelo de decisão (Jev ou Laya) e o registro de cada uma na trilha de decisões.

Usa o cliente assíncrono do SDK: as rotas do FastAPI e os nós do grafo são async, então a chamada
não trava o event loop (sem precisar de asyncio.to_thread).
"""

import time
from functools import lru_cache

from typesafe_sdk import AsyncTypeSafeClient, Question, SystemOneResponse

from config import get_settings


@lru_cache
def get_decision_client() -> AsyncTypeSafeClient:
    settings = get_settings()
    if settings.decision_backend == "laya":
        # O SDK exige uma chave não vazia; o Laya local aceita qualquer uma.
        return AsyncTypeSafeClient(
            base_url=settings.laya_base_url, api_key="laya-local", model="multilingual"
        )
    return AsyncTypeSafeClient()  # lê TYPESAFE_API_KEY do ambiente


async def perguntar_ao_jev(
    no: str, estado: dict, perguntas: dict[str, Question]
) -> tuple[SystemOneResponse, dict]:
    """Uma chamada com todas as perguntas do nó. Devolve a resposta e a entrada da trilha."""
    start = time.perf_counter()
    resposta = await get_decision_client().system_one(state=estado, questions=perguntas)
    latencia_ms = (time.perf_counter() - start) * 1000

    entrada = {
        "tipo": "jev",
        "no": no,
        "modelo": resposta.model,
        "tokens_in": resposta.usage.input_tokens or 0,
        "tokens_out": resposta.usage.output_tokens or 0,
        "latencia_ms": round(latencia_ms, 1),
        "perguntas": [_descrever(nome, resposta) for nome in perguntas],
        "decisao": "",  # preenchida pelo nó depois de aplicar a política
    }
    return resposta, entrada


def evento_de_politica(no: str, decisao: str) -> dict:
    """Uma decisão tomada só pelo código, sem chamar o Jev (cascata, aprovação humana)."""
    return {
        "tipo": "politica",
        "no": no,
        "modelo": "",
        "tokens_in": 0,
        "tokens_out": 0,
        "latencia_ms": 0.0,
        "perguntas": [],
        "decisao": decisao,
    }


def _descrever(nome: str, resposta: SystemOneResponse) -> dict:
    """Resposta e probabilidade de uma pergunta, no formato que o frontend mostra."""
    if nome in resposta.choices:
        a = resposta.choices[nome]
        return {
            "nome": nome,
            "classe": "Choice",
            "resposta": a.choice,
            "probabilidade": round(a.probabilities.get(a.choice, a.confidence), 3),
        }
    if nome in resposta.scores:
        a = resposta.scores[nome]
        topo = max(a.legend)
        return {
            "nome": nome,
            "classe": "Score",
            "resposta": f"{a.score:.2f} de 0 a {topo}",
            "probabilidade": round(a.confidence, 3),
        }
    a = resposta.nouls[nome]
    sim = a.noul >= 0.5
    return {
        "nome": nome,
        "classe": "Noul",
        "resposta": "sim" if sim else "não",
        "probabilidade": round(a.noul if sim else 1 - a.noul, 3),
    }
