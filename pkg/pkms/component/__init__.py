from . import globber
from . import screener
from . import indexer
from . import upserter
from . import resolver
from . import searcher

from typing import Union, Annotated
from pydantic import Field

ComponentUnion = Union[
    globber.GlobberUnion,
    screener.ScreenerUnion,
    indexer.IndexerUnion,
    upserter.UpserterUnion,
    resolver.ResolverUnion,
    searcher.SearcherUnion,
]

ComponentConfigUnion = Annotated[
    Union[
        globber.PathspecGlobberConfig,
        indexer.HtmlIndexerConfig,
        indexer.OdtIndexerConfig,
        indexer.MarkdownIndexerConfig,
        screener.SimpleScreenerConfig,
        upserter.Sqlite3UpserterConfig,
        resolver.UriResolverConfig,
        searcher.Sqlite3SearcherConfig,
    ],
    Field(discriminator="type"),
]

ComponentRuntimeUnion = Union[
    globber.GlobberUnion,
    screener.ScreenerUnion,
    indexer.IndexerUnion,
    upserter.UpserterUnion,
    resolver.ResolverUnion,
    searcher.SearcherUnion,
]

__all__ = [
    'ComponentUnion',
    'ComponentConfigUnion',
    'ComponentRuntimeUnion',
]

from ._ref import make_component_ref_factory

ComponentConfigUnionRef = Annotated[
    Union[str, ComponentConfigUnion],
    make_component_ref_factory(ComponentConfigUnion),
]

__all__ += [
    'ComponentConfigUnioinRef'
]