from abc import ABC, abstractmethod
from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, Union, Dict, List, Literal
from .base import ComponentConfig
from .base import ComponentRuntime
from .base import Component
from ..model import StamperInput
from ..model import StamperOutput

class StamperConfig(Component):
    model_config = ConfigDict(extra="allow", frozen=True)

class StamperRuntime(ComponentRuntime):
    pass

class Stamper(Component):
    Config: type[StamperConfig] = StamperConfig
    Runtime: type[StamperConfig] = StamperRuntime

    def __init__(self, *, config: StamperConfig, runtime: StamperRuntime):
        super().__init__(config=config, runtime=runtime)

    @abstractmethod
    def resolve(self, input:StamperInput) -> StamperOutput:
        ...
