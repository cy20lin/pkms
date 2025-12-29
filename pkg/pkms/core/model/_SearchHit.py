from pydantic import BaseModel, ConfigDict
from typing import Optional


class SearchHit(BaseModel):
    """
    A single search hit.
    """
    model_config = ConfigDict(extra="allow", frozen=True)

    file_id: str
    title: str

    file_uri: Optional[str] = None
    origin_uri: Optional[str] = None

    snippet: Optional[str] = None
    score: Optional[float] = None