from pydantic import BaseModel, Field, ConfigDict
from typing import Optional


class SearchArguments(BaseModel):
    """
    Input arguments for a search operation.
    """
    model_config = ConfigDict(extra="allow")

    query: str = Field(..., min_length=1)
    limit: int = 20
    offset: int = 0