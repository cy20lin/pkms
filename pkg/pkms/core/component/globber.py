from abc import ABC, abstractmethod
from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, Union, Dict, List, Literal
from .base import ComponentConfig
from .base import ComponentRuntime
from .base import Component
from ..model import FileLocation
from ..model import IndexedDocument

class GlobberConfig(ComponentConfig):
    model_config = ConfigDict(extra="forbid")

    patterns: List[str] = Field(
        default=[],
        description="Glob patterns relative to base_path"
    )

    negate: bool = Field(
        default=False,
        description="Negate glob patterns"
    )

class GlobberRuntime(ComponentRuntime):
    pass

class Globber(Component):
    Config: type[GlobberConfig] = GlobberConfig
    Runtime: type[GlobberConfig] = GlobberRuntime

    def __init__(self, *, config: GlobberConfig, runtime: GlobberRuntime):
        super().__init__(config=config, runtime=runtime)

    @abstractmethod
    def glob(self, base_path) -> list[FileLocation]:
        ...
