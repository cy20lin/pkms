from typing import Optional, Dict, List, Literal, Annotated, Union, TypeAlias
from pydantic import BaseModel, ConfigDict, Field
from loguru import logger

from pkms.component.globber import PathspecGlobber
from pkms.component.indexer import HtmlIndexer
from pkms.component.indexer import MarkdownIndexer
from pkms.component.indexer import OdtIndexer
from pkms.component.screener import SimpleScreener
from pkms.component.upserter import Sqlite3Upserter
from pkms.component.resolver import UriResolver
from pkms.component.searcher import Sqlite3Searcher

from ._registry import (
    ComponentRegistry,
    ComponentRegistryConfig,
)
from ._collection import (
    ComponentsConfig,
    CollectionComponents,
    CollectionConfig,
    CollectionRuntime,
    Collection,
)
from pkms.core.component import Component, ComponentConfig, ComponentRuntime
from pkms.component import ComponentConfigUnion
from pkms.core.model import FileLocation

class IngestConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: Optional[str] = None
    description: Optional[str] = None
    components: ComponentRegistryConfig
    collections: List[CollectionConfig] 

IngestState: TypeAlias = IngestConfig
from pkms.core.utility import FileLocationMatcher
from pkms.core.utility import SimpleFileLocationMatcher

class IngestRuntime():
    Config = IngestConfig
    _COMPONENT_CLASS_MAP = {
        'PathspecGlobberConfig': PathspecGlobber,
        'SimpleScreenerConfig': SimpleScreener,
        'Sqlite3UpserterConfig': Sqlite3Upserter,
        'HtmlIndexerConfig': HtmlIndexer,
        'MarkdownIndexerConfig': MarkdownIndexer,
        'OdtIndexerConfig': OdtIndexer,
        'UriResolverConfig': UriResolver,
        'Sqlite3SearcherConfig': Sqlite3Searcher,
    }
    def _update_state(self, state: IngestState|None, config: IngestConfig|None):
        config_dump = config.model_dump() if config else {}
        state_dump = state.model_dump() if state else {}
        merged_dump = {**state_dump, **config_dump}
        updated_state = IngestState.model_validate(merged_dump)
        return updated_state

    def __init__(self, *, config=None, state=None, runtime=None):
        self.base_logger = logger
        self.logger = logger
        self.config : IngestConfig = config
        self._state : IngestState = self._update_state(state, config)
        self.runtime : None = runtime
        self.collections: list[Collection] = []
        self.components = ComponentRegistry()
        self._setup()
        self.collection_location_matcher: FileLocationMatcher = SimpleFileLocationMatcher(
            [c.base_location for c in self.collections]
        )

    def make_component(self, config: ComponentConfigUnion, runtime: Optional[ComponentRuntime]=None):
        return self._COMPONENT_CLASS_MAP[config.type](config=config)
    
    def _setup(self):
        config = self.config
        self.base_logger.debug(f'load config, config.name={config.name}')

        self.components.clear()
        for name, component_config in config.components.items():
            self.components[name] = self.make_component(config=component_config, runtime=None)

        self.collections.clear()
        for collection_config in config.collections:
            collection_components: dict[str,Component] = {}
            ccc = collection_config.components
            ccc_items = [
                ('globber',ccc.globber),
                ('indexer',ccc.indexer),
                ('screener',ccc.screener),
                ('upserter',ccc.upserter),
                ('searcher',ccc.searcher),
                ('resolver',ccc.resolver),
            ]
            for name, component_config in ccc_items:
                if isinstance(component_config, str):
                    key = component_config.lstrip('$')
                    component = self.components[key]
                else:
                    component = self.make_component(config=component_config)
                collection_components[name] = component
            collection = Collection(config=collection_config)
            collection.components = CollectionComponents(**collection_components)
            del collection_components
            self.collections.append(collection)
    
class IngestCapability:
    def __init__(self, runtime: IngestRuntime):
        self.runtime = runtime

    def ingest_workspace(self, dry_run=True) -> int:
        count = 0
        for collection in self.runtime.collections:
            count += collection.ingest(dry_run=dry_run)
        return count

    def ingest_collection(self, collection_location:FileLocation, dry_run=True) -> int:
        count = 0
        index = self.runtime.collection_location_matcher.find_match_index(file_location=collection_location)
        if index is not None:
            collection = self.runtime.collections[index]
            count += collection.ingest(dry_run=dry_run)
        return count

    def ingest_collections(self, collection_locations:list[FileLocation], dry_run=True) -> int:
        count = 0
        for collection_location in collection_locations:
            count += self.ingest_file(file_location=collection_location, dry_run=dry_run)
        return count

    def ingest_file(self, file_location:FileLocation, dry_run=True) -> int:
        count = 0
        index = self.runtime.collection_location_matcher.find_match_index(file_location=file_location)
        if index is not None:
            collection = self.runtime.collections[index]
            count += collection.ingest_file(file_location=file_location, dry_run=dry_run)
        return count

    def ingest_files(self, file_locations:list[FileLocation], dry_run=True) -> int:
        count = 0
        for file_location in file_locations:
            count += self.ingest_file(file_location=file_location, dry_run=dry_run)
        return count