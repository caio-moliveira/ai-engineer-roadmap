from fastapi import APIRouter, HTTPException, Depends, Form, UploadFile, File
from pydantic import BaseModel
from typing import List, Optional
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.runnables import RunnableConfig
from langfuse.langchain import CallbackHandler
from src.settings import settings
from fastapi import Form, UploadFile, File
import json
from src.pdf_utils import load_pdf_from_bytes
from src.chat.chat import chat
from src.customlogger import setup_logger

logger = setup_logger(__name__)

router = APIRouter()

class ChatRequest(BaseModel):
    query: str
    history: Optional[List[dict]] = []

class ChatResponse(BaseModel):
    response: str

@router.post("/chat/ask", response_model=ChatResponse, tags=["Chat"])
async def ask_chat(
    query: str = Form(...),
    collection_name: str = Form("Fiscap_Edital_v1"),
    session_id: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None),
    history: Optional[str] = Form(None),
    clear_history: bool = Form(False)
):
    """
    Endpoint checks information.
    Accepts a file to be used as context.
    """
    try:
        # 1. Process History
        chat_history = []
        
        # If clear_history is True, we effectively ignore any passed history, 
        # starting a fresh session from the backend's perspective for this request.
        if clear_history:
             logger.info("Clear history flag received. Starting with empty history.")
        elif history:
            try:
                history_list = json.loads(history)
                for msg in history_list:
                    role = msg.get("role")
                    content = msg.get("content")
                    if role == "user":
                        chat_history.append(HumanMessage(content=content))
                    elif role == "assistant":
                        chat_history.append(AIMessage(content=content))
            except json.JSONDecodeError:
                logger.warning("Failed to decode history JSON")

        # 2. Process File
        file_text_content = None
        if file:
            logger.info(f"Processing file: {file.filename}")
            if file.filename.lower().endswith('.pdf'):
                content_bytes = await file.read()
                # load_pdf_from_bytes returns (text, num_pages)
                text, _ = load_pdf_from_bytes(content_bytes)
                file_text_content = text
            else:
                # Basic text fallback
                content_bytes = await file.read()
                file_text_content = content_bytes.decode('utf-8', errors='ignore')

        logger.info(f"Received query for Chat: {query}")
        
        
        response_message = await chat.gerar_resposta(
            consulta=query,
            collection_name=collection_name,
            chat_history=chat_history,
            file_content=file_text_content,
            session_id=session_id
        )
        
        return ChatResponse(response=response_message.content)

    except Exception as e:
        logger.error(f"Error in Chat Fiscap: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
