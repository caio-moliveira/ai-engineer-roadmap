from fastapi import APIRouter, UploadFile, File, Form, HTTPException, status
from typing import Literal, List

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
    files: List[UploadFile] = File(...),
    chunk_size: int = Form(1000),
    overlap_chunk: int = Form(100),
    splitter_type: Literal["recursive", "character"] = Form("recursive"),
    use_tiktoken: bool = Form(False)
):
    if not await qdrant_service.collection_exists(collection_name):
        raise HTTPException(status_code=404, detail="Collection not found")

    results = []

    for file in files:
        filename = file.filename

        if await qdrant_service.document_exists(collection_name, filename):
            logger.info(f"Document '{filename}' already exists in '{collection_name}'. Skipping.")
            results.append({
                "filename": filename,
                "status": "skipped",
                "message": "Document already exists in the collection."
            })
            continue

        file_content = await file.read()

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
            
            if not points:
                results.append({
                    "filename": filename,
                    "status": "skipped",
                    "message": "No text could be extracted from the document."
                })
                continue

            await qdrant_service.upsert_vectors(collection_name, points)
            results.append({
                "filename": filename,
                "status": "success",
                "message": "Document successfully ingested.",
                "vector_count": len(points)
            })
        except Exception as e:
            logger.error(f"Error ingesting document '{filename}': {e}")
            results.append({
                "filename": filename,
                "status": "error",
                "message": str(e)
            })

    return {"status": "completed", "results": results}

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
