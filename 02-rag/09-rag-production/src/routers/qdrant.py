from fastapi import APIRouter, UploadFile, File, Form, HTTPException, status
from typing import Literal

from src.embedder.client import QdrantService
from src.embedder.processor import DocumentProcessor
from src.customlogger import setup_logger

logger = setup_logger(__name__)

router = APIRouter(prefix="/qdrant", tags=["Qdrant Management"])
qdrant_service = QdrantService()
doc_processor = DocumentProcessor()

@router.post("/collection")
async def create_collection(collection_name: str):
    created = await qdrant_service.create_collection(collection_name)
    if not created:
        raise HTTPException(status_code=400, detail="Collection already exists")
    return {"status": "success", "message": f"Collection '{collection_name}' created."}

@router.delete("/collection/{collection_name}")
async def delete_collection(collection_name: str):
    await qdrant_service.delete_collection(collection_name)
    return {"status": "success", "message": f"Collection '{collection_name}' deleted."}

@router.post("/collection/{collection_name}/document")
async def insert_document(
    collection_name: str,
    file: UploadFile = File(...),
    chunk_size: int = Form(1000),
    overlap_chunk: int = Form(100),
    splitter_type: Literal["recursive", "character"] = Form("recursive"),
    use_tiktoken: bool = Form(False)
):
    if not await qdrant_service.collection_exists(collection_name):
        raise HTTPException(status_code=404, detail="Collection not found")

    file_content = await file.read()
    filename = file.filename

    logger.info(f"Processing '{filename}' for collection '{collection_name}' with {splitter_type} splitter (chunk:{chunk_size}/overlap:{overlap_chunk}/tiktoken:{use_tiktoken})")

    try:
        points = doc_processor.process_document(
            file_content=file_content, 
            filename=filename,
            chunk_size=chunk_size,
            overlap_chunk=overlap_chunk,
            splitter_type=splitter_type,
            use_tiktoken=use_tiktoken
        )
        await qdrant_service.upsert_vectors(collection_name, points)
        return {"status": "success", "message": f"Document '{filename}' successfully ingested vectors.", "vector_count": len(points)}
    except Exception as e:
        logger.error(f"Error ingesting document '{filename}': {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/collection/{collection_name}/document/{filename}")
async def update_document(
    collection_name: str,
    filename: str,
    file: UploadFile = File(...),
    chunk_size: int = Form(1000),
    overlap_chunk: int = Form(100),
    splitter_type: Literal["recursive", "character"] = Form("recursive"),
    use_tiktoken: bool = Form(False)
):
    """Updates a document by entirely replacing its vectors."""
    if not await qdrant_service.collection_exists(collection_name):
        raise HTTPException(status_code=404, detail="Collection not found")

    # Ensure to use the requested filename specifically
    file_content = await file.read()
    
    try:
        await qdrant_service.delete_document(collection_name, filename)
        points = doc_processor.process_document(
            file_content=file_content, 
            filename=filename,
            chunk_size=chunk_size,
            overlap_chunk=overlap_chunk,
            splitter_type=splitter_type,
            use_tiktoken=use_tiktoken
        )
        await qdrant_service.upsert_vectors(collection_name, points)
        return {"status": "success", "message": f"Document '{filename}' replaced.", "vector_count": len(points)}
    except Exception as e:
        logger.error(f"Error updating document '{filename}': {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/collection/{collection_name}/document/{filename}")
async def delete_document(collection_name: str, filename: str):
    if not await qdrant_service.collection_exists(collection_name):
        raise HTTPException(status_code=404, detail="Collection not found")

    try:
        await qdrant_service.delete_document(collection_name, filename)
        return {"status": "success", "message": f"Document '{filename}' deleted from '{collection_name}'."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
