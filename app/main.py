"""
FastAPI Application - College RAG System

Production-ready entry point with:
- Async lifespan for startup/shutdown
- Versioned API routing
- CORS middleware
- Structured logging

Note: The React frontend is served separately by Vite.
The API endpoints are available at /api/v1/
"""

import logging
from contextlib import asynccontextmanager
from typing import Any, Dict

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

from app.api.dependencies import set_rag_service
from app.api.v1.router import api_router
from app.core.config import get_settings
from app.services.rag_service import RAGService


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: initialize and tear down services."""
    settings = get_settings()

    rag_service = RAGService(settings)
    await rag_service.initialize()
    set_rag_service(rag_service)
    logger.info("Application started")

    yield

    await rag_service.shutdown()
    logger.info("Application shut down")


app = FastAPI(
    title="College RAG System API",
    description="RAG-powered Q&A API for a technical college",
    version="2.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")


@app.get("/", response_class=HTMLResponse)
async def root():
    """
    Root endpoint - indicates that the frontend is served separately.
    
    The React frontend is served by Vite on a separate port.
    Run: cd frontend && npm run dev
    """
    return HTMLResponse(
        content="""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>College RAG System</title>
            <style>
                body {
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    height: 100vh;
                    margin: 0;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                }
                .container {
                    text-align: center;
                    background: white;
                    padding: 40px;
                    border-radius: 8px;
                    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
                }
                h1 {
                    color: #667eea;
                    margin-bottom: 10px;
                }
                p {
                    color: #666;
                    margin-bottom: 8px;
                }
                .api-link {
                    color: #764ba2;
                    text-decoration: none;
                    font-weight: 500;
                }
                .api-link:hover {
                    text-decoration: underline;
                }
                .note {
                    font-size: 14px;
                    color: #999;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>College RAG System API</h1>
                <p>REST API endpoints are available at:</p>
                <p><a href="/api/v1/docs" class="api-link">/api/v1/docs</a> (Swagger UI)</p>
                <p><a href="/api/v1/openapi.json" class="api-link">/api/v1/openapi.json</a> (OpenAPI Schema)</p>
                <hr>
                <p class="note">The React frontend is served separately by Vite.</p>
                <p class="note">To start the frontend, run:</p>
                <pre style="background: #f5f5f5; padding: 15px; border-radius: 4px;">
cd frontend
npm run dev</pre>
            </div>
        </body>
        </html>
        """
    )


@app.get("/api/v1/health")
async def health_check() -> Dict[str, Any]:
    """Quick health check without service dependency."""
    return {
        "status": "healthy",
        "message": "RAG System API is running",
    }


if __name__ == "__main__":
    import uvicorn

    settings = get_settings()
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=True,
    )
