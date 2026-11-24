"""Projeto final: API do agente de operações de vendas com decisões tipadas (Jev + LangGraph).

Rode de dentro da pasta (imports flat):
    cd 06-decision-models/05-final-project
    python main.py                  # API + frontend em http://127.0.0.1:8010

Documentação interativa da API: http://127.0.0.1:8010/docs
Outra porta: defina APP_PORT (ex.: $env:APP_PORT = "8020" no PowerShell).
"""

import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI

import ingest
import tools
from config import get_settings
from database import banco_existe
from frontend import router as frontend_router
from router import router as agente_router

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
logging.getLogger("httpx").setLevel(logging.WARNING)  # uma linha por requisição HTTP é ruído
logger = logging.getLogger("agente")


@asynccontextmanager
async def lifespan(_app: FastAPI):
    settings = get_settings()
    if settings.decision_backend == "jev" and not os.environ.get("TYPESAFE_API_KEY"):
        raise RuntimeError("Defina TYPESAFE_API_KEY no .env da raiz, ou rode com DECISION_BACKEND=laya.")

    if not banco_existe():
        logger.info("[Início] vendas.db não encontrado: rodando a ingestão")
        ingest.main()

    logger.info("[Início] decisões: %s · LLM pequeno: %s · LLM grande: %s · versão padrão: %s",
                settings.decision_backend, settings.llm_small, settings.llm_large, settings.agent_version)
    logger.info("[Início] tools do agente: %s", ", ".join(tools.POR_NOME))
    yield


app = FastAPI(
    title="Agente de Operações de Vendas",
    description="Decisões de controle no Jev (roteador, guardião, juiz); o LLM só escreve.",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(agente_router)
app.include_router(frontend_router)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=get_settings().app_port, reload=True)
