from typing import Dict, Optional
from pydantic import BaseModel, HttpUrl

class AuthHeaders(BaseModel):
    """Custom headers for authentication"""
    headers: Dict[str, str]

class BasicAuth(BaseModel):
    """Basic authentication credentials"""
    username: str
    password: str

class URLInput(BaseModel):
    """Input model for document embedding"""
    url: HttpUrl
    call_name: str
    auth_headers: Optional[AuthHeaders] = None
    basic_auth: Optional[BasicAuth] = None

class QueryInput(BaseModel):
    """Input model for document retrieval"""
    query: str
    top_k: int = 5
    group_by_doc: bool = True 