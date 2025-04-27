import requests
from bs4 import BeautifulSoup
from sentence_transformers import SentenceTransformer
from semantic_text_splitter import TextSplitter
from app.config.settings import MODEL_NAME
from fastapi import HTTPException
from typing import List

class TextService:
    def __init__(self):
        self.model = SentenceTransformer(MODEL_NAME)
        self.splitter = TextSplitter(1500)

    def extract_text_from_url(self, url: str) -> str:
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

    def chunk_text(self, text: str) -> List[str]:
        return list(self.splitter.chunks(text))

    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        return self.model.encode(texts).tolist() 