import requests
from bs4 import BeautifulSoup
from sentence_transformers import SentenceTransformer
from semantic_text_splitter import TextSplitter
from app.config.settings import MODEL_NAME
from fastapi import HTTPException
from typing import List, Optional
from app.models.schemas import AuthHeaders, BasicAuth

class TextService:
    def __init__(self):
        self.model = SentenceTransformer(MODEL_NAME)
        self.splitter = TextSplitter(1500)
        self.chunk_size = 150  # Number of words per chunk

    def extract_text_from_url(self, url: str, auth_headers: Optional[AuthHeaders] = None, basic_auth: Optional[BasicAuth] = None) -> str:
        """
        Extract text content from a URL with optional authentication
        """
        try:
            # Prepare request parameters
            request_kwargs = {
                'url': url,
                'headers': {},
                'auth': None,
                'timeout': 30
            }

            # Add custom headers if provided
            if auth_headers:
                request_kwargs['headers'].update(auth_headers.headers)

            # Add basic auth if provided
            if basic_auth:
                request_kwargs['auth'] = (basic_auth.username, basic_auth.password)

            # Make the request
            response = requests.get(**request_kwargs)
            response.raise_for_status()

            # Parse HTML content
            soup = BeautifulSoup(response.text, 'html.parser')

            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()

            # Get text content
            text = soup.get_text()

            # Clean up text: remove extra whitespace and empty lines
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = ' '.join(chunk for chunk in chunks if chunk)

            return text

        except requests.RequestException as e:
            raise ValueError(f"Error fetching URL: {str(e)}")
        except Exception as e:
            raise ValueError(f"Error processing text: {str(e)}")

    def chunk_text(self, text: str) -> List[str]:
        """
        Split text into chunks of approximately chunk_size words
        """
        words = text.split()
        chunks = []
        
        for i in range(0, len(words), self.chunk_size):
            chunk = ' '.join(words[i:i + self.chunk_size])
            if chunk:  # Only add non-empty chunks
                chunks.append(chunk)
        
        return chunks

    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for a list of text chunks
        """
        try:
            embeddings = self.model.encode(texts)
            return embeddings.tolist()
        except Exception as e:
            raise ValueError(f"Error generating embeddings: {str(e)}") 