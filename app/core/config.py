"""
Application configuration using pydantic-settings.
All settings are loaded from environment variables or .env file.
"""

from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings with environment variable support."""

    # OpenRouter Settings
    OPENROUTER_API_KEY: str = ""
    OPENROUTER_MODEL: str = "meta-llama/llama-3.1-8b-instruct"
    OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1"
    USE_OPENROUTER: bool = True

    # Ollama Settings (fallback)
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    LLM_MODEL: str = "llama3"
    EMBEDDING_MODEL: str = "nomic-embed-text"

    # ChromaDB Settings
    CHROMA_DB_PATH: str = "./database/chroma_db"
    COLLECTION_NAME: str = "college_documents"

    # Document Settings
    DOCUMENTS_PATH: str = "./data/documents"
    CHUNK_SIZE: int = 500
    CHUNK_OVERLAP: int = 50

    # RAG Settings
    TOP_K_RESULTS: int = 3
    TEMPERATURE: float = 0.7

    # Server Settings
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # JWT Settings
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    model_config = {
        "env_prefix": "RAG_",
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": True,
    }


@lru_cache()
def get_settings() -> Settings:
    """Cached settings instance. Call this to get app configuration."""
    return Settings()
