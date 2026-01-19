from ._UriResolver import (
    UriResolver,
    UriResolverConfig,
    UriResolverRuntime,
)

from typing import Union, Annotated
from pydantic import Field

ResolverUnion = Union[
    UriResolver,
]
ResolverConfigUnion = Annotated[
    Union[
        UriResolverConfig,
    ],
    Field(discriminator="type"),
]
ResolverRuntimeUnion = Union[
    UriResolverRuntime,
]

__all__ = [
    'UriResolver',
    'UriResolverConfig',
    'UriResolverRuntime',
    'ResolverUnion',
    'ResolverConfigUnion',
    'ResolverRuntimeUnion',
]

from .._ref import make_component_ref_factory

ResolverConfigUnionRef = Annotated[
    Union[str, ResolverConfigUnion],
    make_component_ref_factory(ResolverConfigUnion),
]

__all__ += [
    'ResolverConfigUnioinRef'
]