from qdrant_client import QdrantClient
from qdrant_client.http import models
from app.config.settings import QDRANT_URL, QDRANT_PORT, QDRANT_COLLECTION_NAME
import uuid
from typing import List, Optional, Dict, Any

class QdrantService:
    def __init__(self):
        self.client = QdrantClient(QDRANT_URL, port=QDRANT_PORT)
        self.collection_name = QDRANT_COLLECTION_NAME
        self._ensure_collection_exists()

    def _ensure_collection_exists(self):
        try:
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=models.VectorParams(
                    size=384,  # Dimension of the embeddings
                    distance=models.Distance.COSINE
                )
            )
        except Exception as e:
            print(f"Collection might already exist: {e}")

    def get_existing_doc_id(self, url: str) -> Optional[str]:
        try:
            search_results = self.client.scroll(
                collection_name=self.collection_name,
                scroll_filter=models.Filter(
                    must=[
                        models.FieldCondition(
                            key="url",
                            match=models.MatchValue(value=str(url))
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

    def delete_document_chunks(self, doc_id: str):
        try:
            self.client.delete(
                collection_name=self.collection_name,
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

    def upsert_points(self, points: List[Dict[str, Any]]):
        self.client.upsert(
            collection_name=self.collection_name,
            points=points
        )

    def search_points(self, query_vector: List[float], limit: int):
        return self.client.query_points(
            collection_name=self.collection_name,
            query=query_vector,
            limit=limit
        ) 