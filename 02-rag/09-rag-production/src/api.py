import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.models import AskRequest, AskResponse
from src.chat.chat import chat
from src.routers import qdrant, chat as chat_router

app = FastAPI(title="Agentic RAG Qdrant API", version="0.1.0")
app.include_router(qdrant.router)
app.include_router(chat_router.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logger = logging.getLogger(__name__)

@app.get("/health")
def healthcheck():
    return {"status": "ok"}
