from fastapi import APIRouter, HTTPException

from endpoint import generate_text_openai, generate_text_langchain
from models import GenerateRequest  

router = APIRouter()    


@router.post("/openai")
async def endpoint_openai(request: GenerateRequest):
    """
    Endpoint que usa a implementação pura da OpenAI.
    """
    try:
        result = await generate_text_openai(request.capital)
        return {"response": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/langchain")
async def endpoint_langchain(request: GenerateRequest):
    """
    Endpoint que usa LangChain. 
    O 'topic' é usado para gerar dicas de produtividade.
    """
    try:
        result = await generate_text_langchain(request.capital)
        return {"response": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
