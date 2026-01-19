from ._PathspecGlobber import (
    PathspecGlobber,
    PathspecGlobberConfig,
    PathspecGlobberRuntime,
)

from typing import Union, Annotated
from pydantic import Field

GlobberUnion = Union[
    PathspecGlobber,
]
GlobberConfigUnion = Annotated[
    Union[
        PathspecGlobberConfig,
    ],
    Field(discriminator="type"),
]
GlobberRuntimeUnion = Union[
    PathspecGlobberRuntime,
]

__all__ = [
    'PathspecGlobber',
    'PathspecGlobberConfig',
    'PathspecGlobberRuntime',
    'GlobberUnion',
    'GlobberConfigUnion',
    'GlobberRuntimeUnion',
]

from .._ref import make_component_ref_factory

GlobberConfigUnionRef = Annotated[
    Union[str, GlobberConfigUnion],
    make_component_ref_factory(GlobberConfigUnion),
]

__all__ += [
    'GlobberConfigUnioinRef'
]