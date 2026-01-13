from abc import ABC, abstractmethod
from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, Union, Dict, List, Literal
from .base import ComponentConfig
from .base import ComponentRuntime
from .base import Component
from ..model import ResolverInput
from ..model import ResolverOutput

class ResolverConfig():
    model_config = ConfigDict(extra="allow", frozen=True)

class ResolverRuntime(ComponentRuntime):
    pass

class Resolver(Component):
    Config: type[ResolverConfig] = ResolverConfig
    Runtime: type[ResolverConfig] = ResolverRuntime

    def __init__(self, *, config: ResolverConfig, runtime: ResolverRuntime):
        super().__init__(config=config, runtime=runtime)

    @abstractmethod
    def resolve(self, input:ResolverInput) -> ResolverOutput:
        ...
