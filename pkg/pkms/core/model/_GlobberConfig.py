from __future__ import annotations

from typing import Optional, Dict, List, Literal
from pydantic import BaseModel, ConfigDict, Field


class GlobberConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    patterns: List[str] = Field(
        ...,
        # min_length=1,
        description="Glob patterns relative to base_path"
    )

    # exclude: List[str] = Field(
    #     default_factory=list,
    #     description="Exclude glob patterns"
    # )