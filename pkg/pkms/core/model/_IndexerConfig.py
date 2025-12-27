from __future__ import annotations

from typing import Optional, Dict, List, Literal
from pydantic import BaseModel, ConfigDict, Field

class IndexerConfig(BaseModel):
    model_config = ConfigDict(extra="allow", frozen=True)


