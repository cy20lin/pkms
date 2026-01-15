from __future__ import annotations

from typing import Optional, Dict, List, Literal, Any
from pydantic import BaseModel, ConfigDict, Field

class ResolvedTarget(BaseModel):
    file_id: str
    file_uri: str
    file_kind: Optional[str]
    title: Optional[str]