# College RAG System

A Retrieval-Augmented Generation (RAG) system for college document Q&A using Ollama and ChromaDB.

## Architecture

- **Backend**: FastAPI with Ollama LLM and ChromaDB vector storage
- **Frontend**: React with Ant Design UI components

## Setup

### Backend
```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows

# Install dependencies
pip install -r requirements.txt

# Start Ollama server
ollama serve

# Pull required models
ollama pull llama3
ollama pull nomic-embed-text

# Run FastAPI server
uvicorn app.main:app --reload
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

## Configuration

Copy `.env.example` to `.env` and configure:
- Ollama settings (default: localhost:11434)
- ChromaDB path
- Document processing settings

## Usage

1. Upload PDF/TXT documents via the web interface
2. Documents are automatically chunked and embedded
3. Ask questions about the uploaded documents
4. Get AI-generated answers with source citations

## Features

- Document upload and processing
- Vector search with embeddings
- LLM-powered question answering
- Source citation tracking
- System statistics dashboard