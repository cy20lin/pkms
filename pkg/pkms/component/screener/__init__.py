from ._SimpleScreener import (
    SimpleScreener,
    SimpleScreenerConfig,
    SimpleScreenerRuntime,
)

from typing import Union, Annotated
from pydantic import Field

ScreenerUnion = Union[
    SimpleScreener,
]
ScreenerConfigUnion = Annotated[
    Union[
        SimpleScreenerConfig,
    ],
    Field(discriminator="type"),
]
ScreenerRuntimeUnion = Union[
    SimpleScreenerRuntime,
]

__all__ = [
    'SimpleScreener',
    'SimpleScreenerConfig',
    'SimpleScreenerRuntime',
    'ScreenerUnion',
    'ScreenerConfigUnion',
    'ScreenerRuntimeUnion',
]

from .._ref import make_component_ref_factory

ScreenerConfigUnionRef = Annotated[
    Union[str, ScreenerConfigUnion],
    make_component_ref_factory(ScreenerConfigUnion),
]

__all__ += [
    'ScreenerConfigUnioinRef'
]