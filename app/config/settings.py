import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Qdrant configuration
QDRANT_URL = os.getenv("QDRANT_URL", "localhost")
QDRANT_PORT = int(os.getenv("QDRANT_PORT", "6333"))
QDRANT_COLLECTION_NAME = os.getenv("QDRANT_COLLECTION_NAME", "documents")

# Model configuration
MODEL_NAME = 'sentence-transformers/all-MiniLM-L6-v2' 