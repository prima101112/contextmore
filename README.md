# RAG Qdrant Test

A FastAPI application for document embedding and retrieval using Qdrant vector database.

## Prerequisites

- Python 3.8+
- Qdrant server running locally or accessible via network

## Setup

1. Create and activate a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the root directory with the following content:
```
QDRANT_URL=localhost
QDRANT_PORT=6333
QDRANT_COLLECTION_NAME=documents
```

## Running the Application

1. Make sure Qdrant server is running. If not, you can run it using Docker:
```bash
docker run -p 6333:6333 qdrant/qdrant
```

2. Start the FastAPI application:
```bash
uvicorn app.main:app --reload
```

3. Access the application at http://localhost:8000

## API Endpoints

- `GET /`: Home page
- `GET /embed`: Embed documents page
- `GET /retrieve`: Retrieve information page
- `POST /embed`: Embed a document from a URL
- `POST /retrieve`: Retrieve information based on a query

## Project Structure

```
app/
├── main.py              # FastAPI application entry point
├── config/
│   └── settings.py      # Configuration settings
├── models/
│   └── schemas.py       # Pydantic models
├── services/
│   ├── qdrant_service.py # Qdrant database operations
│   └── text_service.py   # Text processing operations
└── utils/
```

## Features

- **Embed Documents**: Accepts a URL, extracts text, chunks it, and stores embeddings in Qdrant.
- **Retrieve Documents**: Retrieves relevant document chunks based on a query.

## Example Usage

### Embedding a Document
```bash
curl -X POST "http://localhost:8000/embed" -H "Content-Type: application/json" -d '{"url": "https://example.com"}'
```

### Retrieving Documents
```bash
curl -X POST "http://localhost:8000/retrieve" -H "Content-Type: application/json" -d '{"query": "Your query here", "top_k": 5}'
```

## License
MIT 