from ._HtmlIndexer import (
    HtmlIndexer,
    HtmlIndexerConfig,
    HtmlIndexerRuntime,
)

from ._MarkdownIndexer import (
    MarkdownIndexer,
    MarkdownIndexerConfig,
    MarkdownIndexerRuntime,
)

from ._OdtIndexer import (
    OdtIndexer,
    OdtIndexerConfig,
    OdtIndexerRuntime,
)

from typing import Union, Annotated
from pydantic import Field

IndexerUnion = Union[
    HtmlIndexer,
    MarkdownIndexer,
    OdtIndexer,
]
IndexerConfigUnion = Annotated[
    Union[
        HtmlIndexerConfig,
        MarkdownIndexerConfig,
        OdtIndexerConfig,
    ],
    Field(discriminator="type"),
]
IndexerRuntimeUnion = Union[
    HtmlIndexerRuntime,
    MarkdownIndexerRuntime,
    OdtIndexerRuntime,
]

__all__ = [
    'HtmlIndexer',
    'MarkdownIndexer',
    'OdtIndexer',
    'HtmlIndexerConfig',
    'MarkdownIndexerConfig',
    'OdtIndexerConfig',
    'HtmlIndexerRuntime',
    'MarkdownIndexerRuntime',
    'OdtIndexerRuntime',
    'IndexerUnion',
    'IndexerConfigUnion',
    'IndexerRuntimeUnion',
]

from .._ref import make_component_ref_factory

IndexerConfigUnionRef = Annotated[
    Union[str, IndexerConfigUnion],
    make_component_ref_factory(IndexerConfigUnion),
]

__all__ += [
    'IndexerConfigUnioinRef'
]