from ._Sqlite3Upserter import (
    Sqlite3Upserter,
    Sqlite3UpserterConfig,
    Sqlite3UpserterRuntime,
)

from typing import Union, Annotated
from pydantic import Field

UpserterUnion = Union[
    Sqlite3Upserter,
]
UpserterConfigUnion = Annotated[
    Union[
        Sqlite3UpserterConfig,
    ],
    Field(discriminator="type"),
]
UpserterRuntimeUnion = Union[
    Sqlite3UpserterRuntime,
]

__all__ = [
    'Sqlite3Upserter',
    'Sqlite3UpserterConfig',
    'Sqlite3UpserterRuntime',
    'UpserterUnion',
    'UpserterConfigUnion',
    'UpserterRuntimeUnion',
]

from .._ref import make_component_ref_factory

UpserterConfigUnionRef = Annotated[
    Union[str, UpserterConfigUnion],
    make_component_ref_factory(UpserterConfigUnion),
]

__all__ += [
    'UpserterConfigUnioinRef'
]