from fastapi import FastAPI, Request, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from datetime import datetime
import uuid
from typing import List, Dict, Any

from app.models.schemas import URLInput, QueryInput
from app.services.qdrant_service import QdrantService
from app.services.text_service import TextService
from fastapi_mcp import FastApiMCP

app = FastAPI()

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Initialize templates
templates = Jinja2Templates(directory="templates")

# Initialize services
qdrant_service = QdrantService()
text_service = TextService()

@app.get("/")
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {
        "request": request,
        "year": datetime.now().year
    })

@app.get("/embed")
async def get_embed_page(request: Request):
    return templates.TemplateResponse("embed.html", {
        "request": request,
        "year": datetime.now().year
    })

@app.get("/retrieve")
async def get_retrieve_page(request: Request):
    return templates.TemplateResponse("retrieve.html", {
        "request": request,
        "year": datetime.now().year
    })

@app.post("/embed")
async def embed_document(url_input: URLInput):
    # Check if URL already exists
    existing_doc_id = qdrant_service.get_existing_doc_id(url_input.url)
    
    try:
        # Extract and process text with authentication if provided
        text = text_service.extract_text_from_url(
            url=str(url_input.url),
            auth_headers=url_input.auth_headers,
            basic_auth=url_input.basic_auth
        )
        chunks = text_service.chunk_text(text)
        embeddings = text_service.generate_embeddings(chunks)
        
        # Generate a unique document ID (reuse if updating)
        doc_id = existing_doc_id if existing_doc_id else str(uuid.uuid4())
        current_date = datetime.now().isoformat()
        
        # If updating, delete existing chunks first
        if existing_doc_id:
            qdrant_service.delete_document_chunks(doc_id)
        
        # Prepare points for Qdrant
        points = []
        for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
            points.append(
                {
                    "id": str(uuid.uuid4()),
                    "vector": embedding,
                    "payload": {
                        "text": chunk,
                        "url": str(url_input.url),
                        "call_name": url_input.call_name,
                        "doc_id": doc_id,
                        "chunk_id": i,
                        "date": current_date,
                        "total_chunks": len(chunks)
                    }
                }
            )
        
        # Store in Qdrant
        qdrant_service.upsert_points(points)
        
        return {
            "message": f"Successfully {'updated' if existing_doc_id else 'embedded'} {len(chunks)} chunks from {url_input.url}",
            "doc_id": doc_id,
            "call_name": url_input.call_name,
            "date": current_date,
            "is_update": existing_doc_id is not None
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.post("/retrieve")
async def retrieve_documents(query_input: QueryInput):
    # Generate embedding for the query
    query_embedding = text_service.generate_embeddings([query_input.query])[0]
    
    # Search in Qdrant
    search_results = qdrant_service.search_points(
        query_vector=query_embedding,
        limit=query_input.top_k * 4
    )
    
    if query_input.group_by_doc:
        # Group results by document
        doc_results = {}
        for hit in search_results.points:
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
            doc_results[doc_id]["chunks"].sort(key=lambda x: x["chunk_id"])
        
        results = list(doc_results.values())
        results.sort(key=lambda x: x["avg_score"], reverse=True)
        return {"results": results}
    else:
        # Return individual chunks without grouping
        results = []
        for hit in search_results.points:
            results.append({
                "text": hit.payload["text"],
                "url": hit.payload["url"],
                "call_name": hit.payload["call_name"],
                "doc_id": hit.payload["doc_id"],
                "chunk_id": hit.payload["chunk_id"],
                "date": hit.payload["date"],
                "score": hit.score
            })
        
        results.sort(key=lambda x: x["score"], reverse=True)
        return {"results": results}

# Mount MCP routes
mcp = FastApiMCP(app)
mcp.mount() 