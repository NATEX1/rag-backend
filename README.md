# RAG Backend

FastAPI backend for College RAG system with Ollama and ChromaDB.

## Setup

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start Ollama server
ollama serve

# Pull models
ollama pull llama3
ollama pull nomic-embed-text

# Run server
uvicorn app.main:app --reload
```

## API Endpoints

- `GET /api/v1/health` - Health check
- `GET /api/v1/stats` - System statistics
- `POST /api/v1/documents/upload` - Upload document
- `POST /api/v1/questions/ask` - Ask question