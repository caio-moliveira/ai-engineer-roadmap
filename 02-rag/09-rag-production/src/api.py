import logging
from fastapi import FastAPI
from fastapi.responses import JSONResponse

from src.models import AskRequest, AskResponse
from src.agent_graph import run_agent

app = FastAPI(title="Agentic RAG Qdrant API", version="0.1.0")

logger = logging.getLogger(__name__)

@app.get("/health")
def healthcheck():
    return {"status": "ok"}

@app.post("/ask", response_model=AskResponse)
def ask_endpoint(req: AskRequest):
    try:
        response = run_agent(
            user_query=req.question,
            session_id=req.session_id,
            top_k=req.top_k,
            collection_hint=req.collection_hint,
            metadata_filters=req.metadata_filters
        )
        return response
    except Exception as e:
        logger.error(f"Error executing agent: {str(e)}", exc_info=True)
        return JSONResponse(status_code=503, content={"detail": f"Service unavailable: {str(e)}"})
