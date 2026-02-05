"""API v1 router - aggregates all v1 endpoint routers."""

from fastapi import APIRouter

from app.api.v1.endpoints import documents, health, questions

api_router = APIRouter()

api_router.include_router(
    questions.router,
    prefix="/query",
    tags=["Questions"],
)
api_router.include_router(
    documents.router,
    prefix="/documents",
    tags=["Documents"],
)
api_router.include_router(
    health.router,
    tags=["Health"],
)
