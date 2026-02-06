"""Document upload and management endpoints."""

import logging
import os

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status

from app.api.dependencies import get_rag_service
from app.core.config import Settings, get_settings
from app.schemas.document import DocumentUploadResponse
from app.services.rag_service import RAGService

logger = logging.getLogger(__name__)
router = APIRouter()

ALLOWED_EXTENSIONS = (".pdf", ".txt")


@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    rag: RAGService = Depends(get_rag_service),
    settings: Settings = Depends(get_settings),
) -> DocumentUploadResponse:
    """
    Upload a PDF or TXT document for indexing.
    
    Authentication temporarily disabled for development.

    The document is saved to disk, split into chunks, embedded,
    and stored in ChromaDB for later retrieval.
    """
    filename = file.filename or "unknown"

    if not filename.endswith(ALLOWED_EXTENSIONS):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Only {', '.join(ALLOWED_EXTENSIONS)} files are supported.",
        )

    try:
        file_path = os.path.join(settings.DOCUMENTS_PATH, filename)

        content = await file.read()
        with open(file_path, "wb") as f:
            f.write(content)

        result = await rag.load_document(file_path, filename)
        return DocumentUploadResponse(**result)

    except Exception as e:
        logger.exception("Error uploading document: %s", filename)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error uploading document: {e}",
        )
