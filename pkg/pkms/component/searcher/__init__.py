from ._Sqlite3Searcher import (
    Sqlite3Searcher,
    Sqlite3SearcherConfig,
    Sqlite3SearcherRuntime,
)

from typing import Union, Annotated
from pydantic import Field

SearcherUnion = Union[
    Sqlite3Searcher,
]
SearcherConfigUnion = Annotated[
    Union[
        Sqlite3SearcherConfig,
    ],
    Field(discriminator="type"),
]
SearcherRuntimeUnion = Union[
    Sqlite3SearcherRuntime,
]

__all__ = [
    'Sqlite3Searcher',
    'Sqlite3SearcherConfig',
    'Sqlite3SearcherRuntime',
    'SearcherUnion',
    'SearcherConfigUnion',
    'SearcherRuntimeUnion',
]

from .._ref import make_component_ref_factory

SearcherConfigUnionRef = Annotated[
    Union[str, SearcherConfigUnion],
    make_component_ref_factory(SearcherConfigUnion),
]

__all__ += [
    'SearcherConfigUnioinRef'
]