"""Rotas da API do agente. A lógica fica em service.py; aqui só HTTP."""

from fastapi import APIRouter, HTTPException

import service
import tools
from config import get_settings
from schemas import AprovacaoIn, PerguntaIn, ResumoOut, RespostaOut

router = APIRouter(prefix="/agente", tags=["Agente"])


@router.post("/perguntas", response_model=RespostaOut)
async def criar_pergunta(entrada: PerguntaIn):
    """Faz uma pergunta ao agente. Se o guardião pedir aprovação, a resposta volta com
    `status = aguardando_aprovacao` e o `thread_id` para retomar."""
    return await service.perguntar(entrada)


@router.post("/perguntas/{thread_id}/aprovacao", response_model=RespostaOut)
async def responder_aprovacao(thread_id: str, entrada: AprovacaoIn):
    """Aprova ou recusa a ação que pausou o grafo, e retoma a execução."""
    try:
        return await service.aprovar(thread_id, entrada.aprovado)
    except KeyError:
        raise HTTPException(status_code=404, detail="Conversa não encontrada")
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc))


@router.get("/resumo", response_model=ResumoOut)
def ler_resumo():
    """Quantas perguntas o modelo pequeno resolveu sozinho e quanto isso economizou."""
    return service.resumo()


@router.get("/ferramentas")
def listar_ferramentas():
    """As tools que o agente pode propor: as de leitura e as de risco (simuladas)."""
    return [
        {"nome": t.name, "descricao": t.description, "argumentos": t.args, "risco": t in tools.RISCO}
        for t in tools.ferramentas(incluir_acoes_de_risco=True)
    ]


@router.get("/acoes-executadas")
def listar_acoes_executadas():
    """Os reembolsos e cancelamentos gravados no banco depois de passar pelo guardião."""
    return tools.acoes_executadas()


@router.get("/config")
def ler_config():
    """Backend de decisão, modelos e versão padrão (sem chaves)."""
    s = get_settings()
    return {
        "decision_backend": s.decision_backend,
        "llm_small": s.llm_small,
        "llm_large": s.llm_large,
        "agent_version": s.agent_version,
    }
