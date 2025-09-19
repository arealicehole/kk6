# KK6 Transcript Synthesis

A system to process and analyze Gilbert's phone transcripts for mentions of "Kanna Kickback" using AI and vector similarity search.

## Features

- <� **Transcript Processing**: Analyze text files for Kanna Kickback mentions using OpenRouter/Ollama LLMs
- =� **Vector Database**: Store transcripts with embeddings in PostgreSQL + pgvector
- =� **Chat Interface**: ChatGPT-like web interface to query transcripts with natural language
- <� **Kickback Filter**: Toggle to filter results to only transcripts mentioning Kanna Kickback
- = **Vector Search**: Semantic similarity search using nomic-embed-text embeddings

## Architecture

- **Backend**: Python with FastAPI
- **Database**: PostgreSQL with pgvector extension
- **LLMs**: OpenRouter API (primary) + Ollama (local fallback)
- **Embeddings**: Ollama nomic-embed-text model (768 dimensions)
- **Frontend**: HTML/CSS/JavaScript chat interface
- **Package Management**: UV (modern Python package manager)

## Quick Start

1. **Install dependencies**: `uv sync`
2. **Start database**: `docker-compose up -d`
3. **Add embeddings**: `uv run python add_embeddings.py`
4. **Start chat**: `uv run python chat_server.py`
5. **Open**: http://localhost:8080

## Results

Successfully processed **62 Gilbert transcripts** with:
-  **5 transcripts** mention Kanna Kickback (confidence scores: 0.5-0.9)
-  **100% embedding coverage** (768-dimensional vectors)
-  **Vector similarity search** enabled
-  **Web chat interface** with Kickback filter toggle

## Related Systems

- **[KK6 Planning Database](../kk6-planning-database/)**: Dedicated event planning database that uses extracted information from these transcripts
- This transcript synthesis system serves as a source for the planning database's automated extraction process

See full documentation for detailed setup and usage instructions.