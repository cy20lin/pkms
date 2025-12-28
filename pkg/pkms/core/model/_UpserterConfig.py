from __future__ import annotations

from typing import Optional, Dict, List, Literal
from pydantic import BaseModel, ConfigDict, Field

class UpserterConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    db_path: str = Field(
        ...,
        description="Path to database"
    )
