import io
import time
import httpx
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from typing import Literal
from azure.core.credentials import AzureKeyCredential
from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.core.exceptions import HttpResponseError

from module.config.settings import settings
from module.database import save_task_result


router = APIRouter(prefix='/api/v1/azure', tags=['Azure Proxy'])

@router.post("/convert")
async def analyze_read(file: UploadFile = File(...)):
    # Validação básica de extensão
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="O arquivo deve ser um PDF.")

    client = DocumentIntelligenceClient(endpoint=settings.AZURE_ENDPOINT, credential=AzureKeyCredential(settings.AZURE_KEY))
    start_time = time.perf_counter()

    try:
        # Lendo o conteúdo do upload diretamente para a memória
        content_bytes = await file.read()
        
        # O SDK aceita bytes diretamente no parâmetro 'body'
        poller = client.begin_analyze_document(
            "prebuilt-read",
            body=content_bytes,
            content_type="application/pdf"
        )
        result = poller.result()
        execution_time = time.perf_counter() - start_time

        # Salvar no Histórico
        save_task_result(
            task_id=f"azure-{int(time.time()*1000)}",
            filename=file.filename,
            engine="azure-di",
            model="prebuilt-read",
            pages=len(result.pages),
            execution_time=round(execution_time, 4),
            status="success",
        )

        return {"text": result.content}

    except HttpResponseError as e:
        raise HTTPException(status_code=500, detail=f"Erro no Azure Document Intelligence: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

