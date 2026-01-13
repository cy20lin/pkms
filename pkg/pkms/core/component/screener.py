from abc import ABC, abstractmethod
from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, Union, Dict, List, Literal, Iterable
from .base import ComponentConfig
from .base import ComponentRuntime
from .base import Component
from ..model import ScreeningResult
from ..model import ScreenCandidate

class ScreenerConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")
    type: str = Field(..., discriminator="type")

class ScreenerRuntime(ComponentRuntime):
    pass

class Screener(Component):
    """
    Screener examines candidate files and decides
    whether they are admitted into the ingestion pipeline.
    
    Screener implementations MAY consult the provided runtime for shared state or resource access,
    but MUST function correctly without it.
    """

    # Should be override in derived class
    name: str = None
    # Screener Config
    Config: type[ScreenerConfig]= ScreenerConfig
    # Runtime/Context used by the screener 
    # for external states and resource management
    Runtime: type[ScreenerRuntime] = ScreenerRuntime


    def __init__(self, *, config: ScreenerConfig, runtime: Optional[ScreenerRuntime] = None):
        self.config = config
        assert self.name == config.name

    @abstractmethod
    def screen(
        self,
        candidates: Iterable[ScreenCandidate],
    ) -> List[ScreeningResult]:
        """
        Screen candidate files.

        - Must NOT perform indexing
        - Must NOT perform database writes
        - Must return explicit screening decisions

        :param candidates: iterable of ScreenCandidate
        :return: list of ScreeningResult (order-preserving)
        """
        raise NotImplementedError