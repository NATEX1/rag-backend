"""Question/query endpoints."""

import logging

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies import get_rag_service
from app.schemas.answer import AnswerResponse
from app.schemas.question import QuestionRequest
from app.services.rag_service import RAGService

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("", response_model=AnswerResponse)
async def ask_question(
    request: QuestionRequest,
    rag: RAGService = Depends(get_rag_service),
) -> AnswerResponse:
    """
    Ask a question and receive a RAG-generated answer.

    The system embeds the question, retrieves relevant document chunks,
    and generates an answer using the configured LLM.
    """
    try:
        result = await rag.query(request.question)
        return AnswerResponse(**result)
    except Exception as e:
        logger.exception("Error processing question")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing question: {e}",
        )
