
from abc import ABC, abstractmethod
from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, Union, Dict, List, Literal
from .base import ComponentConfig
from .base import ComponentRuntime
from .base import Component
from ..model import IndexedDocument

class UpserterConfig(ComponentConfig):
    model_config = ConfigDict(extra="allow")

    db_path: str = Field(
        ...,
        description="Path to database"
    )

class UpserterRuntime(ComponentRuntime):
    pass

class Upserter(Component):
    Config: type[UpserterConfig] = UpserterConfig
    Runtime: type[UpserterConfig] = UpserterRuntime

    def __init__(self, *, config: UpserterConfig, runtime: UpserterRuntime):
        super().__init__(config=config, runtime=runtime)

    @abstractmethod
    def upsert(self, doc: IndexedDocument) -> None:
        ...
