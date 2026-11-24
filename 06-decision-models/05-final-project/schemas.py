"""Contratos da API (request e response), em Pydantic."""

from typing import Literal

from pydantic import BaseModel, Field


# --- Requests ------------------------------------------------------------------------------------
class PerguntaIn(BaseModel):
    pergunta: str = Field(min_length=1, examples=["Qual foi o faturamento do mês atual?"])
    versao: Literal["v1", "v2", "v3"] | None = Field(
        None, description="versão do grafo; vazio usa AGENT_VERSION (padrão v3)"
    )
    modelo_inicial: Literal["auto", "pequeno", "grande"] = Field(
        "auto", description="auto deixa o roteador escolher; pequeno ou grande força o modelo da 1ª tentativa"
    )
    contexto: str | None = Field(
        None, description="a pergunta anterior, quando esta mensagem responde a um pedido de esclarecimento"
    )


class AprovacaoIn(BaseModel):
    aprovado: bool


# --- Responses -----------------------------------------------------------------------------------
class PerguntaJev(BaseModel):
    nome: str
    classe: Literal["Choice", "Score", "Noul"]
    resposta: str
    probabilidade: float


class EntradaTrilha(BaseModel):
    tipo: Literal["jev", "politica"]
    no: str
    modelo: str
    tokens_in: int
    tokens_out: int
    latencia_ms: float
    perguntas: list[PerguntaJev]
    decisao: str
    acao: str = ""  # só no guardião: a tool que ele avaliou


class ChamadaLLM(BaseModel):
    etapa: str
    modelo: str
    tamanho: Literal["pequeno", "grande"]
    tokens_in: int
    tokens_out: int
    latencia_ms: float


class Passo(BaseModel):
    acao: str
    argumentos: dict
    resultado: str
    status: Literal["executada", "bloqueada", "recusada"]


class AprovacaoPendente(BaseModel):
    acao: str
    argumentos: dict
    motivo: str


class Totais(BaseModel):
    jev_chamadas: int
    jev_tokens_in: int
    jev_tokens_out: int
    jev_latencia_ms: float
    llm_chamadas: int
    llm_tokens_in: int
    llm_tokens_out: int
    llm_latencia_ms: float
    llm_custo_usd: float


class RespostaOut(BaseModel):
    thread_id: str
    versao: Literal["v1", "v2", "v3"]
    status: Literal["concluida", "esclarecimento", "aguardando_aprovacao"]
    resposta: str = ""
    aviso: str = ""
    intencao: str = ""
    modelo: str = ""
    tentativas: int = 0
    aprovacao_pendente: AprovacaoPendente | None = None
    passos: list[Passo] = []
    trilha: list[EntradaTrilha] = []
    chamadas_llm: list[ChamadaLLM] = []
    totais: Totais


class ResumoOut(BaseModel):
    perguntas: int = Field(description="perguntas concluídas desde que a API subiu")
    resolvidas_pelo_pequeno: int = Field(description="respondidas pelo modelo pequeno, sem cascata nem aviso")
    cascatas: int = Field(description="respostas que o juiz mandou refazer no modelo grande")
    bloqueios: int = Field(description="ações barradas pelo guardião")
    aprovacoes_humanas: int
    jev_chamadas: int
    jev_latencia_media_ms: float
    llm_chamadas_pequeno: int
    llm_chamadas_grande: int
    custo_real_usd: float
    custo_se_tudo_no_grande_usd: float
    economia_usd: float
    economia_pct: float
