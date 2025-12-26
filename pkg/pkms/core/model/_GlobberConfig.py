from __future__ import annotations

from typing import Optional, Dict, List, Literal
from pydantic import BaseModel, ConfigDict, Field


class GlobberConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    patterns: List[str] = Field(
        default=[],
        description="Glob patterns relative to base_path"
    )

    negate: bool = Field(
        default=False,
        description="Negate glob patterns"
    )