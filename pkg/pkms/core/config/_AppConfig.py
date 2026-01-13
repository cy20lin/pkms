from __future__ import annotations

from typing import Optional, Dict, List, Literal
from pydantic import BaseModel, ConfigDict, Field

from ._CollectionConfig import CollectionConfig
from ._IndexerBuildingConfig import IndexerBuildingConfig

class AppConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    version: str = Field(
        ...,
        description="Config schema version (semver)"
    )

    name: Optional[str] = None
    description: Optional[str] = None

    indexer_mapping: Dict[str, IndexerBuildingConfig] = Field(
        default_factory=dict,
        description="Global indexer mapping (extension -> config)"
    )

    collections: List[CollectionConfig] = Field(
        ...,
        min_length=1,
        description="List of collections to index"
    )