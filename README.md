# ContextMore

ContextMore is a FastAPI application for document embedding and semantic retrieval, powered by the Qdrant vector database. It allows you to embed documents from URLs (with or without authentication), chunk and vectorize their content, and perform semantic search over your knowledge base.

## Why

Many companies want to integrate their internal documentation / PRD with tools like Cursor, Copilot to make them easy to provide more context to the toolings, or other MCP clients. However, embedding documents into a centralized internal knowledge base often requires building complex workflows, and different teams use different sources of context. 

ContextMore is designed to solve this problem by providing a simple, centralized context library that is accessible via API (for building internal tools) and is MCP server ready. The goal is not only to support document embedding, but also to eventually support internal repositories and code libraries (coming soon).

---

## Features

- **Embed Documents**: Extracts text from a given URL (supports authentication), splits it into chunks, generates embeddings, and stores them in Qdrant.
- **Semantic Retrieval**: Retrieve the most relevant document chunks or grouped documents based on a natural language query.
- **Web UI**: User-friendly web interface for embedding and searching documents.
- **API Access**: RESTful endpoints for programmatic access.
- **MCP Server support*: Supporting mcp server using fastapi-mcp.

---

## Prerequisites

- Python 3.8+
- Docker (for running Qdrant locally)
- (Optional) Qdrant server running locally or accessible via network

---

## Quick Start

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd contextmore
```

### 2. Set Up Python Environment

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the root directory:

```
QDRANT_URL=localhost
QDRANT_PORT=6333
QDRANT_COLLECTION_NAME=documents
```

### 5. Run Qdrant (Vector Database)

You can run Qdrant locally using Docker:

```bash
./runqdrant.sh
```

Or manually:

```bash
docker run -p 6333:6333 qdrant/qdrant
```

---

## Running the Application

### Development Server

```bash
uvicorn app.main:app --reload
```

Or, for graceful shutdown and advanced handling:

```bash
python run.py
```

The app will be available at [http://localhost:8000](http://localhost:8000).

---

## API Endpoints

### Web Pages

- `GET /` — Home page
- `GET /embed` — Embed documents via web UI
- `GET /retrieve` — Search and retrieve via web UI

### REST API

- `POST /embed` — Embed a document from a URL  
  **Request Body:**  
  ```json
  {
    "url": "https://example.com",
    "call_name": "Example Document",
    "auth_headers": { "headers": { "Authorization": "Bearer ..." } }, // optional
    "basic_auth": { "username": "user", "password": "pass" } // optional
  }
  ```
  **Response:**  
  - Success message, document ID, and metadata.

- `POST /retrieve` — Retrieve information based on a query  
  **Request Body:**  
  ```json
  {
    "query": "Your search query",
    "top_k": 5,                // optional, default 5
    "group_by_doc": true       // optional, default true
  }
  ```
  **Response:**  
  - List of relevant document chunks or grouped documents.

---

## Authentication Support

- **Basic Auth**: Provide username and password for HTTP Basic Authentication.
- **Custom Headers**: Supply any custom headers (e.g., Bearer tokens) for authenticated requests.

---

## Project Structure

```
contextmore/
├── app/
│   ├── main.py                # FastAPI application entry point
│   ├── config/
│   │   └── settings.py        # Environment and model settings
│   ├── models/
│   │   └── schemas.py         # Pydantic request/response models
│   ├── services/
│   │   ├── qdrant_service.py  # Qdrant database operations
│   │   └── text_service.py    # Text extraction, chunking, embedding
│   └── utils/                 # (Reserved for future utilities)
├── static/                    # Static files (logo, CSS, etc.)
├── templates/                 # Jinja2 HTML templates for web UI
├── run.py                     # Custom server runner with graceful shutdown
├── runqdrant.sh               # Script to run Qdrant via Docker
├── requirements.txt           # Python dependencies
└── README.md                  # This documentation
```

---

## Example Usage

### Embedding a Document via API

```bash
curl -X POST "http://localhost:8000/embed" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com", "call_name": "Example"}'
```

### Retrieving Documents via API

```bash
curl -X POST "http://localhost:8000/retrieve" \
  -H "Content-Type: application/json" \
  -d '{"query": "Your query here", "top_k": 5}'
```

---

## Dependencies

- fastapi
- uvicorn
- python-dotenv
- qdrant-client
- sentence-transformers
- semantic-text-splitter
- requests
- beautifulsoup4
- jinja2

(See `requirements.txt` for exact versions.)

---

## License

MIT

---

**ContextMore** makes it easy to build your own knowledge base with semantic search and MCP ready, using only URLs and a vector database.
For questions or contributions, please open an issue or pull request! 

---

## Embeding URLS (Team Workspace)

### embeding public url

for embeding public urls just put the url on the API embed or from the UI

### Embeding confluence url (atlassian)

Embeding atlassian confluence workspace you need to know the ID and a personal api token as a password for confluence.

using basic auth to the url 
https://{confluence url}/wiki/api/v2/pages?id={page-id}&body-format=storage
username : your email (usualy)
password : personal api token [docs personal access token](https://developer.atlassian.com/server/jira/platform/personal-access-token/)

put bthat on contextmore and your internal docs will be embeded

### EMbeding Coda url