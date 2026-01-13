from abc import ABC, abstractmethod
from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, Union, Dict, List, Literal
from .base import ComponentConfig
from .base import ComponentRuntime
from .base import Component
from ..model import SearchArguments
from ..model import SearchResult

class SearcherConfig(ComponentConfig):
    """
    Configuration for Searcher initialization.
    """
    model_config = ConfigDict(extra="allow")
    db_path: str
    default_limit: int = 20
    max_limit: int = 100


class SearcherRuntime(ComponentRuntime):
    pass


class Searcher(Component):
    """
    Abstract base class for all searchers.
    """
    Config: type[SearcherConfig] = SearcherConfig
    Runtime: type[SearcherConfig] = SearcherRuntime

    def __init__(self, *, config: SearcherConfig, runtime: SearcherRuntime):
        super().__init__(config=config, runtime=runtime)

    @abstractmethod
    def search(self, args: SearchArguments) -> SearchResult:
        """
        Execute a search query.
        """
        raise NotImplementedError