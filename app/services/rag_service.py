"""
RAG Service - Core business logic for the RAG pipeline.

Responsibilities:
- Document chunking and embedding
- Vector storage via ChromaDB
- Query processing and LLM-powered answer generation

Now supports both Ollama (local) and OpenRouter (cloud) LLM providers.
"""

import logging
from typing import Dict, List, Optional

import chromadb
import httpx
import ollama
from chromadb.config import Settings as ChromaSettings
from pypdf import PdfReader

from app.core.config import Settings

logger = logging.getLogger(__name__)


class RAGService:
    """
    Service layer for RAG operations.

    Encapsulates all retrieval-augmented generation logic:
    embedding, vector storage, retrieval, and LLM generation.
    """

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._collection: Optional[chromadb.Collection] = None
        self._client: Optional[chromadb.PersistentClient] = None
        self._http_client: Optional[httpx.AsyncClient] = None

    async def initialize(self) -> None:
        """Initialize ChromaDB connection and HTTP client. Called during app startup."""
        import os

        logger.info("Initializing RAG service...")
        
        # Initialize HTTP client for OpenRouter
        if self._settings.USE_OPENROUTER:
            self._http_client = httpx.AsyncClient(
                base_url=self._settings.OPENROUTER_BASE_URL,
                headers={
                    "Authorization": f"Bearer {self._settings.OPENROUTER_API_KEY}",
                    "Content-Type": "application/json",
                },
                timeout=None,
            )
            logger.info("OpenRouter client initialized (model: %s)", self._settings.OPENROUTER_MODEL)

        os.makedirs(self._settings.CHROMA_DB_PATH, exist_ok=True)
        os.makedirs(self._settings.DOCUMENTS_PATH, exist_ok=True)

        self._client = chromadb.PersistentClient(
            path=self._settings.CHROMA_DB_PATH,
            settings=ChromaSettings(anonymized_telemetry=False),
        )

        self._collection = self._client.get_or_create_collection(
            name=self._settings.COLLECTION_NAME,
            metadata={"description": "College technical documents"},
        )

        doc_count = self._collection.count()
        logger.info(
            "ChromaDB connected (documents in system: %d)", doc_count
        )

    async def shutdown(self) -> None:
        """Cleanup on application shutdown."""
        logger.info("Shutting down RAG service.")
        if self._http_client:
            await self._http_client.aclose()
        self._client = None
        self._collection = None

    @property
    def collection(self) -> chromadb.Collection:
        if self._collection is None:
            raise RuntimeError(
                "RAG service not initialized. Call initialize() first."
            )
        return self._collection

    # ------------------------------------------------------------------
    # Embedding (using Ollama for embeddings)
    # ------------------------------------------------------------------

    def _get_embedding(self, text: str) -> List[float]:
        """Generate a vector embedding via Ollama."""
        try:
            response = ollama.embeddings(
                model=self._settings.EMBEDDING_MODEL,
                prompt=text,
            )
            return response["embedding"]
        except Exception:
            logger.exception("Failed to create embedding")
            raise

    # ------------------------------------------------------------------
    # LLM Generation (using OpenRouter or Ollama)
    # ------------------------------------------------------------------

    async def _generate_llm_response(self, prompt: str) -> str:
        """Generate response using OpenRouter or Ollama based on settings."""
        if self._settings.USE_OPENROUTER and self._http_client:
            return await self._generate_openrouter(prompt)
        else:
            return await self._generate_ollama(prompt)

    async def _generate_openrouter(self, prompt: str) -> str:
        """Generate response using OpenRouter API."""
        try:
            response = await self._http_client.post(
                "/chat/completions",
                json={
                    "model": self._settings.OPENROUTER_MODEL,
                    "messages": [
                        {"role": "system", "content": "You are a helpful assistant for a technical college. Answer based on the provided context. Format your response using Markdown with proper headings, bullet points, and emphasis for better readability."},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": self._settings.TEMPERATURE,
                    "max_tokens": 2000,
                }
            )
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]
        except Exception as e:
            logger.exception("OpenRouter API error")
            raise RuntimeError(f"OpenRouter API error: {e}")

    async def _generate_ollama(self, prompt: str) -> str:
        """Generate response using Ollama (fallback)."""
        try:
            response = ollama.generate(
                model=self._settings.LLM_MODEL,
                prompt=prompt,
                options={"temperature": self._settings.TEMPERATURE},
            )
            return response["response"]
        except Exception:
            logger.exception("Ollama generation error")
            raise

    # ------------------------------------------------------------------
    # Text chunking
    # ------------------------------------------------------------------

    def _split_text(self, text: str) -> List[str]:
        """Split text into overlapping chunks with smart boundary detection."""
        chunks: List[str] = []
        start = 0
        text_length = len(text)
        chunk_size = self._settings.CHUNK_SIZE
        overlap = self._settings.CHUNK_OVERLAP

        while start < text_length:
            end = start + chunk_size

            # Find a natural break point near the end
            if end < text_length:
                for i in range(end, start, -1):
                    if text[i] in (" ", "\n", ".", "!", "?", ")", "}", "]"):
                        end = i + 1
                        break

            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)

            start = end - overlap

        return chunks

    # ------------------------------------------------------------------
    # Document loading
    # ------------------------------------------------------------------

    def _read_pdf(self, file_path: str) -> str:
        """Extract text from a PDF file with Thai text normalization."""
        reader = PdfReader(file_path)
        text = "".join(page.extract_text() or "" for page in reader.pages)
        return self._normalize_thai_text(text)

    def _normalize_thai_text(self, text: str) -> str:
        """
        Normalize Thai text to fix common extraction issues.
        
        Fixes:
        - Tone marks extracted as numbers (e.g., ่ -> 3)
        - Incorrect character spacing
        - Normalization of Thai Unicode
        """
        import unicodedata
        
        # Common PDF extraction issues with Thai tone marks
        # Tone mark ่ (MAI THO) sometimes extracted as '3'
        # Tone mark ้ (MAI EK) sometimes extracted as '4'
        # Tone mark ๊ (MAI TRI) sometimes extracted as '5'
        # Tone mark ๋ (MAI CHATTAWA) sometimes extracted as '6'
        
        replacements = {
            '3': '่',  # MAI THO
            '4': '้',  # MAI EK
            '5': '๊',  # MAI TRI
            '6': '๋',  # MAI CHATTAWA
        }
        
        # First, normalize Unicode to decomposed form
        text = unicodedata.normalize('NFC', text)
        
        # Fix common extraction errors
        # When tone marks are between consonant and vowel, they might be extracted as numbers
        # Pattern: consonant + number + vowel -> consonant + tone_mark + vowel
        import re
        
        # Thai consonants and vowels (all Thai characters except tone marks)
        thai_chars = 'กขฃคฅฆงจฉชซฌญฎฏฐฑฒณดตถทธนบปผฝพฟภมยรลวศษสหฬอฮะาิีึืุูัํฤฦๅๆ็์'
        
        # Replace numbers that should be tone marks
        # This is a heuristic - numbers between Thai characters are likely tone marks
        result = []
        chars = list(text)
        
        for i, char in enumerate(chars):
            if char in replacements:
                # Check if this number is surrounded by Thai characters
                # Look back for any Thai character (skip over existing tone marks/spaces)
                prev_is_thai = False
                for j in range(i-1, -1, -1):
                    if chars[j] in thai_chars:
                        prev_is_thai = True
                        break
                    elif chars[j] not in '่้๊๋์ ':  # Skip existing tone marks and spaces
                        break
                
                # Look forward for any Thai character
                next_is_thai = False
                for j in range(i+1, len(chars)):
                    if chars[j] in thai_chars:
                        next_is_thai = True
                        break
                    elif chars[j] not in '่้๊๋์ ':  # Skip existing tone marks and spaces
                        break
                
                # If between Thai chars, it's likely a tone mark
                if prev_is_thai and next_is_thai:
                    result.append(replacements[char])
                else:
                    result.append(char)
            else:
                result.append(char)
        
        return ''.join(result)

    async def load_document(self, file_path: str, filename: str) -> Dict:
        """
        Load a document into the RAG system.

        Reads the file, chunks it, generates embeddings, and stores
        everything in ChromaDB.
        """
        logger.info("Loading document: %s", filename)

        try:
            # Read file content
            if filename.endswith(".pdf"):
                text = self._read_pdf(file_path)
            elif filename.endswith(".txt"):
                with open(file_path, "r", encoding="utf-8") as f:
                    text = self._normalize_thai_text(f.read())
            else:
                return {
                    "success": False,
                    "message": "Only .pdf and .txt files are supported.",
                }

            # Chunk
            chunks = self._split_text(text)
            logger.info("Split document into %d chunks", len(chunks))

            # Generate IDs and metadata
            ids = [f"{filename}_chunk_{i}" for i in range(len(chunks))]
            metadatas: List[Dict[str, str | int]] = [
                {"source": filename, "chunk_id": i} for i in range(len(chunks))
            ]

            # Embed and store
            logger.info("Generating embeddings and storing in vector DB...")
            embeddings = [self._get_embedding(chunk) for chunk in chunks]

            self.collection.add(
                ids=ids,
                embeddings=embeddings,  # type: ignore[arg-type]
                documents=chunks,
                metadatas=metadatas,  # type: ignore[arg-type]
            )

            logger.info("Document loaded successfully (%d chunks)", len(chunks))

            return {
                "success": True,
                "message": "Document loaded successfully.",
                "filename": filename,
                "chunks_created": len(chunks),
            }

        except Exception as e:
            logger.exception("Error loading document: %s", filename)
            return {
                "success": False,
                "message": f"Error loading document: {e}",
            }

    # ------------------------------------------------------------------
    # Query / RAG pipeline
    # ------------------------------------------------------------------

    async def query(self, question: str) -> Dict:
        """
        Full RAG pipeline:
        1. Embed the question
        2. Retrieve similar chunks from ChromaDB
        3. Build a prompt with context
        4. Generate an answer via LLM (OpenRouter or Ollama)
        """
        logger.info("Query: %s", question)

        try:
            if self.collection.count() == 0:
                return {
                    "question": question,
                    "answer": (
                        "No documents in the system yet. "
                        "Please upload documents first."
                    ),
                    "sources": [],
                    "confidence": 0.0,
                }

            # 1. Embed the question
            logger.info("Searching for relevant documents...")
            question_embedding = self._get_embedding(question)

            # 2. Retrieve
            results = self.collection.query(
                query_embeddings=[question_embedding],
                n_results=self._settings.TOP_K_RESULTS,
            )

            relevant_docs = results["documents"][0] if results["documents"] else []
            sources = list(
                {
                    meta["source"]
                    for meta in (results["metadatas"][0] if results["metadatas"] else [])
                    if isinstance(meta, dict) and "source" in meta
                }
            )

            if not relevant_docs:
                return {
                    "question": question,
                    "answer": "No relevant documents found for this question.",
                    "sources": [],
                    "confidence": 0.0,
                }

            logger.info("Found %d relevant documents", len(relevant_docs))

            # 3. Build prompt
            context = "\n\n".join(relevant_docs)
            prompt = self._create_prompt(question, context)

            # 4. Generate answer
            logger.info("Generating answer via LLM (%s)...", 
                       "OpenRouter" if self._settings.USE_OPENROUTER else "Ollama")
            answer = await self._generate_llm_response(prompt)
            logger.info("Answer generated successfully")

            return {
                "question": question,
                "answer": answer,
                "sources": sources,
                "confidence": 0.85,
            }

        except Exception as e:
            logger.exception("Error during query")
            return {
                "question": question,
                "answer": f"Error processing query: {e}",
                "sources": [],
                "confidence": 0.0,
            }

    def _create_prompt(self, question: str, context: str) -> str:
        """Build the LLM prompt with retrieved context."""
        return (
            "You are a helpful assistant for a technical college.\n\n"
            "Instructions:\n"
            "- Answer ONLY from the provided reference documents.\n"
            "- If no relevant information is found, say so.\n"
            "- Answer politely in Thai.\n"
            "- Use Markdown formatting for better readability:\n"
            "  - Use ## for main headings\n"
            "  - Use bullet points (-) for lists\n"
            "  - Use **bold** for emphasis\n"
            "  - Use code blocks (```) for any code or technical terms\n"
            "- Structure your answer with clear sections.\n\n"
            f"Reference documents:\n{context}\n\n"
            f"Question: {question}\n\n"
            "Answer (in Markdown format):"
        )

    # ------------------------------------------------------------------
    # Stats
    # ------------------------------------------------------------------

    def get_stats(self) -> Dict:
        """Return system statistics."""
        llm_provider = "OpenRouter" if self._settings.USE_OPENROUTER else "Ollama"
        llm_model = (self._settings.OPENROUTER_MODEL 
                    if self._settings.USE_OPENROUTER 
                    else self._settings.LLM_MODEL)
        
        return {
            "total_documents": self.collection.count(),
            "collection_name": self._settings.COLLECTION_NAME,
            "embedding_model": self._settings.EMBEDDING_MODEL,
            "llm_provider": llm_provider,
            "llm_model": llm_model,
        }
