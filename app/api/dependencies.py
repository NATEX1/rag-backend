"""
Shared FastAPI dependencies.

Provides dependency-injected access to services and configuration.
"""

from app.core.config import Settings, get_settings
from app.services.rag_service import RAGService

# Singleton service instance, initialized during app lifespan
_rag_service: RAGService | None = None


def get_rag_service() -> RAGService:
    """Dependency: get the RAG service instance."""
    if _rag_service is None:
        raise RuntimeError("RAG service not initialized")
    return _rag_service


def set_rag_service(service: RAGService) -> None:
    """Set the global RAG service (called during lifespan startup)."""
    global _rag_service
    _rag_service = service
