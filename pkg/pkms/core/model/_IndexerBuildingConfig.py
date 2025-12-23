from __future__ import annotations

from typing import Optional, Dict, List, Literal
from pydantic import BaseModel, ConfigDict, Field


class IndexerBuildingConfig(BaseModel):
    """
    Declarative config for constructing an Indexer.
    """
    model_config = ConfigDict(extra="forbid")

    module: str = Field(
        ...,
        description="Python import path to the Indexer class"
    )

    config_base: Optional[Literal["builtin", "global", "default"]] = Field(
        default="default",
        description="Which base config to inherit from"
    )

    config: Dict[str, object] = Field(
        default_factory=dict,
        description="Indexer-specific configuration"
    )