from typing import Optional, Dict, List, Literal, Annotated, Union, TypeAlias
from pydantic import BaseModel, ConfigDict, Field
from loguru import logger as logging

from pkms.component.globber import PathspecGlobber
from pkms.component.indexer import HtmlIndexer
from pkms.component.indexer import MarkdownIndexer
from pkms.component.indexer import OdtIndexer
from pkms.component.screener import SimpleScreener
from pkms.component.upserter import Sqlite3Upserter
from pkms.component.resolver import UriResolver
from pkms.component.searcher import Sqlite3Searcher

from pkms.ingest.registry import (
    ComponentRegistry,
    ComponentRegistryConfig,
)
from pkms.ingest.collection import (
    ComponentsConfig,
    CollectionComponents,
    CollectionConfig,
    CollectionRuntime,
    Collection,
)
from ..core.component import Component, ComponentConfig, ComponentRuntime
from ..component import ComponentConfigUnion

class AppConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: Optional[str] = None
    description: Optional[str] = None
    components: ComponentRegistryConfig
    collections: List[CollectionConfig] 

class App():
    Config = AppConfig
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
    def __init__(self, *, config, runtime=None):
        self.config : AppConfig = config
        self.runtime : None = runtime
        self.collections: list[Collection] = []
        self.components = ComponentRegistry()
        self._setup()

    def make_component(self, config: ComponentConfigUnion, runtime: Optional[ComponentRuntime]=None):
        return self._COMPONENT_CLASS_MAP[config.type](config=config)
    
    def _setup(self):
        config = self.config
        logging.debug(f'load config, config.name={config.name}')

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
    
    def _ingest(self, dry_run):
        for c in self.collections:
            c.ingest(dry_run=dry_run)

    def run(self, dry_run=True):
        self._ingest(dry_run=dry_run)
        
