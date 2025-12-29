from __future__ import annotations
from typing import Optional, Dict, List, Literal
from pydantic import BaseModel, ConfigDict, Field


class SearcherConfig(BaseModel):
    """
    Configuration for Searcher initialization.
    """
    model_config = ConfigDict(extra="allow", frozen=True)

    db_path: str

    default_limit: int = 20
    max_limit: int = 100