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

class GlobberConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    patterns: List[str] = Field(
        ...,
        min_length=1,
        description="Glob patterns relative to base_path"
    )

    # exclude: List[str] = Field(
    #     default_factory=list,
    #     description="Exclude glob patterns"
    # )

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

class UpserterConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    db_path: str = Field(
        ...,
        description="Path to SQLite database"
    )

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