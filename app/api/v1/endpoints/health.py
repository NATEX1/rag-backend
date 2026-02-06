"""Health and stats endpoints."""

from typing import Any, Dict

from fastapi import APIRouter, Depends

from app.api.dependencies import get_rag_service
from app.services.rag_service import RAGService

router = APIRouter()


@router.get("/stats")
async def get_stats(
    rag: RAGService = Depends(get_rag_service),
) -> Dict[str, Any]:
    """Return system statistics (document count, model info)."""
    return rag.get_stats()


@router.get("/health")
async def health_check() -> Dict[str, str]:
    """Health check endpoint."""
    return {
        "status": "healthy",
        "message": "RAG System is running",
    }
