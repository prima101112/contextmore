# RAG Pipeline API

This project implements a Retrieval-Augmented Generation (RAG) pipeline using FastAPI, sentence-transformers, and Qdrant.

## Features

- **Embed Documents**: Accepts a URL, extracts text, chunks it, and stores embeddings in Qdrant.
- **Retrieve Documents**: Retrieves relevant document chunks based on a query.

## Setup

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Start Qdrant**:
   Ensure Qdrant is running locally on port 6333. You can start it using Docker:
   ```bash
   docker run -p 6333:6333 qdrant/qdrant
   ```

3. **Run the FastAPI Application**:
   ```bash
   uvicorn main:app --reload
   ```

## API Endpoints

### Embed Documents
- **Endpoint**: `/embed`
- **Method**: POST
- **Body**:
  ```json
  {
    "url": "https://example.com"
  }
  ```

### Retrieve Documents
- **Endpoint**: `/retrieve`
- **Method**: POST
- **Body**:
  ```json
  {
    "query": "Your query here",
    "top_k": 5
  }
  ```

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