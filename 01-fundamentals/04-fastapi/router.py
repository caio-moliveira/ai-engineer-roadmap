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
        result = await generate_text_openai(request.prompt)
        return {"response": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/langchain")
async def endpoint_langchain(request: GenerateRequest):
    """
    Endpoint que usa LangChain. 
    Se 'topic' for fornecido, usa o template de dica de produtividade.
    Caso contrário, usa o prompt como tópico.
    """
    try:
        # Usa o topic se existir, senão usa o prompt como topic
        topic_input = request.topic if request.topic else request.prompt
        result = await generate_text_langchain(topic_input)
        return {"response": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
