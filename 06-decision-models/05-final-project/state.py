"""O estado que passa pelos nós do grafo."""

import operator
from typing import Annotated, Literal, TypedDict


class AgentState(TypedDict, total=False):
    # Entrada
    pergunta: str
    versao: Literal["v1", "v2", "v3"]
    modelo_inicial: Literal["auto", "pequeno", "grande"]

    # Roteador
    tentativa: int  # 1 na primeira passagem; sobe a cada vez que o juiz manda refazer
    intencao: str  # consulta, acao ou conversa
    tamanho: Literal["pequeno", "grande"]
    modelo: str  # provedor:modelo escolhido para o agente

    # Agente e ferramentas
    passos: Annotated[list[dict], operator.add]  # {acao, argumentos, resultado, status}
    proposta: dict | None  # {acao, argumentos} esperando o guardião
    decisao_guardiao: str  # permitir, aprovacao, bloquear
    motivo_guardiao: str
    aprovado: bool

    # Resposta
    resposta: str
    decisao_juiz: str  # entregar, refazer ou aviso
    feedback_juiz: str
    status: Literal["respondida", "esclarecimento"]
    aviso: str

    # Observabilidade
    trilha: Annotated[list[dict], operator.add]  # cada chamada ao Jev e cada decisão de política
    chamadas_llm: Annotated[list[dict], operator.add]  # tokens e latência de cada chamada ao LLM
