from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests
from bs4 import BeautifulSoup
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.http import models
import os
from typing import List, Optional
from semantic_text_splitter import TextSplitter
from dotenv import load_dotenv
from datetime import datetime
import uuid
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi import Request

# Load environment variables
load_dotenv()

app = FastAPI()

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Initialize templates
templates = Jinja2Templates(directory="templates")

# Initialize the sentence transformer model
model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

# Get Qdrant configuration from environment variables
QDRANT_URL = os.getenv("QDRANT_URL", "localhost")
QDRANT_PORT = int(os.getenv("QDRANT_PORT", "6333"))
QDRANT_COLLECTION_NAME = os.getenv("QDRANT_COLLECTION_NAME", "documents")

# Initialize Qdrant client
qdrant_client = QdrantClient(QDRANT_URL, port=QDRANT_PORT)

# Create collection if it doesn't exist
try:
    qdrant_client.create_collection(
        collection_name=QDRANT_COLLECTION_NAME,
        vectors_config=models.VectorParams(
            size=384,  # Dimension of the embeddings
            distance=models.Distance.COSINE
        )
    )
except Exception as e:
    print(f"Collection might already exist: {e}")

class URLInput(BaseModel):
    url: str
    call_name: str  # A name to easily identify/group documents

class QueryInput(BaseModel):
    query: str
    top_k: Optional[int] = 5
    group_by_doc: Optional[bool] = True  # Whether to group results by document

def get_existing_doc_id(url: str) -> Optional[str]:
    """Get the document ID if the URL already exists."""
    try:
        search_results = qdrant_client.scroll(
            collection_name=QDRANT_COLLECTION_NAME,
            scroll_filter=models.Filter(
                must=[
                    models.FieldCondition(
                        key="url",
                        match=models.MatchValue(value=url)
                    )
                ]
            ),
            limit=1
        )
        if search_results[0]:
            return search_results[0][0].payload["doc_id"]
        return None
    except Exception as e:
        print(f"Error checking URL existence: {e}")
        return None

def delete_document_chunks(doc_id: str):
    """Delete all chunks associated with a document ID."""
    try:
        qdrant_client.delete(
            collection_name=QDRANT_COLLECTION_NAME,
            points_selector=models.FilterSelector(
                filter=models.Filter(
                    must=[
                        models.FieldCondition(
                            key="doc_id",
                            match=models.MatchValue(value=doc_id)
                        )
                    ]
                )
            )
        )
    except Exception as e:
        print(f"Error deleting document chunks: {e}")

@app.get("/")
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/embed")
async def get_embed_page(request: Request):
    return templates.TemplateResponse("embed.html", {"request": request})

@app.get("/retrieve")
async def get_retrieve_page(request: Request):
    return templates.TemplateResponse("retrieve.html", {"request": request})

def extract_text_from_url(url: str) -> str:
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        return soup.get_text()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error fetching URL: {str(e)}")

def chunk_text(text: str) -> List[str]:
    # Initialize the semantic text splitter with a maximum chunk size of 1000 characters
    splitter = TextSplitter(1000)
    # Split the text into semantic chunks
    chunks = splitter.chunks(text)
    return list(chunks)

@app.post("/embed")
async def embed_document(url_input: URLInput):
    # Check if URL already exists
    existing_doc_id = get_existing_doc_id(url_input.url)
    
    # Extract text from URL
    text = extract_text_from_url(url_input.url)
    
    # Chunk the text using semantic text splitter
    chunks = chunk_text(text)
    
    # Generate embeddings for each chunk
    embeddings = model.encode(chunks)
    
    # Generate a unique document ID (reuse if updating)
    doc_id = existing_doc_id if existing_doc_id else str(uuid.uuid4())
    current_date = datetime.now().isoformat()
    
    # If updating, delete existing chunks
    if existing_doc_id:
        delete_document_chunks(doc_id)
    
    # Store in Qdrant
    points = []
    for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
        points.append(
            models.PointStruct(
                id=i,  # Unique ID for each chunk
                vector=embedding.tolist(),
                payload={
                    "text": chunk,
                    "url": url_input.url,
                    "call_name": url_input.call_name,
                    "doc_id": doc_id,
                    "chunk_id": i,
                    "date": current_date,
                    "total_chunks": len(chunks)
                }
            )
        )
    
    qdrant_client.upsert(
        collection_name=QDRANT_COLLECTION_NAME,
        points=points
    )
    
    return {
        "message": f"Successfully {'updated' if existing_doc_id else 'embedded'} {len(chunks)} chunks from {url_input.url}",
        "doc_id": doc_id,
        "call_name": url_input.call_name,
        "date": current_date,
        "is_update": existing_doc_id is not None
    }

@app.post("/retrieve")
async def retrieve_documents(query_input: QueryInput):
    # Generate embedding for the query
    query_embedding = model.encode(query_input.query)
    
    # Search in Qdrant
    search_results = qdrant_client.search(
        collection_name=QDRANT_COLLECTION_NAME,
        query_vector=query_embedding.tolist(),
        limit=query_input.top_k * 4  # Get more results to ensure we have enough unique documents
    )
    
    if query_input.group_by_doc:
        # Group results by document
        doc_results = {}
        for hit in search_results:
            doc_id = hit.payload["doc_id"]
            if doc_id not in doc_results:
                doc_results[doc_id] = {
                    "doc_id": doc_id,
                    "call_name": hit.payload["call_name"],
                    "url": hit.payload["url"],
                    "date": hit.payload["date"],
                    "chunks": [],
                    "total_chunks": hit.payload["total_chunks"],
                    "avg_score": 0
                }
            
            doc_results[doc_id]["chunks"].append({
                "text": hit.payload["text"],
                "chunk_id": hit.payload["chunk_id"],
                "score": hit.score
            })
            doc_results[doc_id]["avg_score"] += hit.score
        
        # Calculate average scores and sort documents
        for doc_id in doc_results:
            doc_results[doc_id]["avg_score"] /= len(doc_results[doc_id]["chunks"])
            # Sort chunks by chunk_id to maintain document order
            doc_results[doc_id]["chunks"].sort(key=lambda x: x["chunk_id"])
        
        # Convert to list and sort by average score
        results = list(doc_results.values())
        results.sort(key=lambda x: x["avg_score"], reverse=True)
        results = results[:query_input.top_k]
        
        return {"results": results}
    else:
        # Return individual chunks without grouping
        results = []
        for hit in search_results:
            results.append({
                "text": hit.payload["text"],
                "url": hit.payload["url"],
                "call_name": hit.payload["call_name"],
                "doc_id": hit.payload["doc_id"],
                "chunk_id": hit.payload["chunk_id"],
                "date": hit.payload["date"],
                "score": hit.score
            })
        
        return {"results": results}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
