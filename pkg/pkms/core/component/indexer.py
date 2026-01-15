from abc import ABC, abstractmethod
from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, Union, Dict, List, Literal
from .base import ComponentConfig
from .base import ComponentRuntime
from .base import Component
from ..model import FileLocation
from ..model import IndexedDocument
from ..model import FileStamp

class IndexerConfig(ComponentConfig):
    model_config = ConfigDict(extra="allow", frozen=True)

class IndexerRuntime(ComponentRuntime):
    pass

class Indexer(Component):
    Config: type[IndexerConfig] = IndexerConfig
    Runtime: type[IndexerConfig] = IndexerRuntime

    def __init__(self, *, config: IndexerConfig, runtime: IndexerRuntime):
        super().__init__(config=config, runtime=runtime)

    @abstractmethod
    def index(self, file_location: FileLocation, file_stamp: FileStamp) -> IndexedDocument:
        ...
