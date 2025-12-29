from pydantic import BaseModel, ConfigDict
from typing import List
from ._SearchHit import SearchHit


class SearchResult(BaseModel):
    """
    Search results with pagination metadata.
    """
    model_config = ConfigDict(extra="allow")
    query: str
    limit: int
    offset: int

    hits: List[SearchHit]