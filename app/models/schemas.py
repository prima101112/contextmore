from pydantic import BaseModel
from typing import Optional

class URLInput(BaseModel):
    url: str
    call_name: str  # A name to easily identify/group documents

class QueryInput(BaseModel):
    query: str
    top_k: Optional[int] = 5
    group_by_doc: Optional[bool] = True  # Whether to group results by document 