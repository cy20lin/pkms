from __future__ import annotations

from typing import Optional, Dict, List, Literal
from pydantic import BaseModel, ConfigDict, Field

from ._IndexerBuildingConfig import IndexerBuildingConfig
from ..component.globber._GlobberConfig import GlobberConfig
from ..component.upserter._UpserterConfig import UpserterConfig


class CollectionConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(
        ...,
        description="Human-readable collection name"
    )

    description: Optional[str] = None

    base_path: str = Field(
        ...,
        description="Filesystem base path for this collection"
    )

    globber: GlobberConfig

    indexer_mapping: Dict[str, IndexerBuildingConfig] = Field(
        default_factory=dict,
        description="Collection-level indexer overrides (extension -> config)"
    )

    upserter: UpserterConfig