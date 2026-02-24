from fastapi import APIRouter, UploadFile, File, HTTPException, status, Form
from pydantic import BaseModel, Field
from typing import List, Optional
import re

from src.embedder.client import QdrantService
from src.embedder.processor import DocumentProcessor

router = APIRouter(tags=["Embeddings & Vector DB"])

# Pydantic Models
class CollectionCreate(BaseModel):
    collection_name: str = Field(..., description="Name of the collection (alphanumeric and underscores only)")

    def validate_name(self):
        if not re.match(r"^[a-zA-Z0-9_]+$", self.collection_name):
            raise ValueError("Collection name must contain only alphanumeric characters and underscores.")
        return self.collection_name

class DocumentResponse(BaseModel):
    filename: str
    status: str
    chunks_processed: Optional[int] = 0

class DocumentsList(BaseModel):
    collection_name: str
    documents: List[str]

# Service Instances
# In a real app, these might be injected dependencies
qdrant_service = QdrantService()
doc_processor = DocumentProcessor()

@router.post("/collections", status_code=status.HTTP_201_CREATED)
async def create_collection(payload: CollectionCreate):
    """
    Creates a new Qdrant collection with default vector size (1536).
    """
    try:
        payload.validate_name()
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    if await qdrant_service.create_collection(payload.collection_name):
        return {"message": f"Collection '{payload.collection_name}' created successfully."}
    else:
        # If it returns False, it likely already exists (based on my implementation)
        # Or we could change implementation to raise error. 
        # Using 409 Conflict if it exists is standard.
        raise HTTPException(status_code=409, detail=f"Collection '{payload.collection_name}' already exists.")

@router.post("/collections/{name}/documents", response_model=DocumentResponse)
async def upload_document(name: str, file: UploadFile = File(...)):
    """
    Uploads and processes a document (PDF/TXT) into the specific collection.
    """
    if not await qdrant_service.collection_exists(name):
        raise HTTPException(status_code=404, detail="Collection not found.")

    if not file.filename:
        raise HTTPException(status_code=400, detail="Filename is missing.")

    content = await file.read()
    
    try:
        points = doc_processor.process_document(content, file.filename)
        await qdrant_service.upsert_vectors(name, points)
        
        return DocumentResponse(
            filename=file.filename,
            status="processed",
            chunks_processed=len(points)
        )
    except Exception as e:
        # Log error in real world
        raise HTTPException(status_code=500, detail=f"Error processing document: {str(e)}")

@router.get("/collections/{name}/documents", response_model=DocumentsList)
async def list_documents(name: str):
    """
    Lists unique documents in a collection.
    """
    if not await qdrant_service.collection_exists(name):
        raise HTTPException(status_code=404, detail="Collection not found.")

    unique_docs = await qdrant_service.list_unique_documents(name)
    return DocumentsList(collection_name=name, documents=unique_docs)

@router.delete("/collections/{name}/documents/{filename}")
async def delete_document(name: str, filename: str):
    """
    Removes a specific document from the collection.
    """
    if not await qdrant_service.collection_exists(name):
        raise HTTPException(status_code=404, detail="Collection not found.")

    await qdrant_service.delete_document(name, filename)
    return {"message": f"Document '{filename}' deleted from collection '{name}'."}
