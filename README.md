# College RAG System

A Retrieval-Augmented Generation (RAG) system for college document Q&A using Ollama and ChromaDB.

## Architecture

This project is split into two separate repositories:

- **rag-backend**: FastAPI with Ollama LLM and ChromaDB vector storage
- **rag-frontend**: React with Ant Design UI components

## Setup

### Backend (rag-backend)
```bash
cd rag-backend

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

### Frontend (rag-frontend)
```bash
cd rag-frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

## Configuration

Copy `rag-backend/.env.example` to `rag-backend/.env` and configure:
- Ollama settings (default: localhost:11434)
- ChromaDB path
- Document processing settings

## Usage

1. Start both backend and frontend servers
2. Upload PDF/TXT documents via the web interface
3. Documents are automatically chunked and embedded
4. Ask questions about the uploaded documents
5. Get AI-generated answers with source citations

## Features

- Document upload and processing
- Vector search with embeddings
- LLM-powered question answering
- Source citation tracking
- System statistics dashboard
- Crimson theme with minimal design

## Repository Structure

```
pic-rag/
├── rag-backend/     # FastAPI backend repository
├── rag-frontend/    # React frontend repository
├── .env            # Local configuration
├── .gitignore      # Git ignore rules
└── README.md       # This file
```

## Deployment

Each repository can be deployed independently:
- Backend: Deploy to any cloud platform supporting Python/FastAPI
- Frontend: Deploy to any static hosting service (Vercel, Netlify, etc.)