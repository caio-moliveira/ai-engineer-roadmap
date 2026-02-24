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

@app.post("/ask", response_model=AskResponse)
async def ask_endpoint(req: AskRequest):
    try:
        response_msg = await chat.gerar_resposta(
            consulta=req.question,
            collection_name=req.collection_name
        )
        
        return AskResponse(
            answer=response_msg.content,
            collection_name=req.collection_name

        )
    except Exception as e:
        logger.error(f"Error executing agent: {str(e)}", exc_info=True)
        return JSONResponse(status_code=503, content={"detail": f"Service unavailable: {str(e)}"})
