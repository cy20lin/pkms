from pkms.component.globber import PathspecGlobber
from pkms.component.indexer import HtmlIndexer
from pkms.component.upserter import Sqlite3Upserter
from pkms.component.screener import SimpleScreener
from pkms.core.model import ScreeningStatus


import commentjson as json
import argparse
import sys
from loguru import logger as logging

def str_to_bool(s: str):
    if s.isupper():
        ss = s.lower()
    else:
        ss = s[0].lower() + s[1:]
    if ss in ('1','y','t','yes','true','on'):
        return True
    elif ss in ('0','n','f','no','false','off'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')


from typing import Optional, Dict, List, Literal, Annotated, Union, TypeAlias
from pydantic import BaseModel, ConfigDict, Field

from pkms.component import ComponentConfigUnion


from pkms.component.globber import GlobberConfigUnionRef
from pkms.component.screener import ScreenerConfigUnionRef
from pkms.component.indexer import IndexerConfigUnionRef
from pkms.component.upserter import UpserterConfigUnionRef
from pkms.component.resolver import ResolverConfigUnionRef
from pkms.component.searcher import SearcherConfigUnionRef
from pkms.core.component import Component

ComponentRegistry = dict[str,Component]

from pkms.component.indexer import IndexerConfigUnion

class ComponentsConfig(BaseModel):
    model_config = ConfigDict(extra="allow")
    globber: GlobberConfigUnionRef
    screener: ScreenerConfigUnionRef
    indexer: IndexerConfigUnionRef
    upserter: UpserterConfigUnionRef
    searcher: SearcherConfigUnionRef
    resolver: ResolverConfigUnionRef

class CollectionConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str
    base_path: str
    description: Optional[str] = None
    components: ComponentsConfig 

ComponentRegistryConfig = Annotated[dict[str,ComponentConfigUnion],dict]
ComponentRegistry = Annotated[dict[str,Component],dict]
class AppConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: Optional[str] = None
    description: Optional[str] = None
    components: ComponentRegistryConfig
    collections: List[CollectionConfig] 

def parse_args(argv:list[str]=None):
    parser = argparse.ArgumentParser("Ingest specified collection of owned file resources")
    parser.add_argument("config_path")
    parser.add_argument('--dry-run', help='Just print instead of renaming the files',default=None, const=True, nargs='?', type=str_to_bool)
    parser.add_argument('--verbose', help='Print Verbosely',default=True, const=True, nargs='?', type=str_to_bool)
    return parser.parse_args(argv[1:])


from pkms.core.component import ComponentRuntime
import pkms.component

class CollectionRuntime():
    pass

from pkms.core.component.globber import Globber
from pkms.core.component.screener import Screener
from pkms.core.component.indexer import Indexer
from pkms.core.component.upserter import Upserter
from pkms.core.component.resolver import Resolver
from pkms.core.component.searcher import Searcher

class CollectionComponents():
    def __init__(self,*, globber, screener, indexer, upserter, resolver, searcher):
        self.globber: Globber = globber
        self.screener: Screener = screener
        self.indexer: Indexer = indexer
        self.upserter: Upserter = upserter
        self.resolver: Resolver = resolver
        self.searcher: Searcher = searcher

class Collection():
    Config = CollectionConfig
    Runtime = None
    def __init__(self, config:CollectionConfig, runtime: Optional[CollectionRuntime]=None):
        self.config = config
        self.runtime = runtime
        self.name = config.name
        self.description = config.description
        self.base_path = config.base_path
        self.components: CollectionComponents 
    
    def ingest(self, dry_run:bool|None=False):
        print(f'collection: name={self.name}, base_path={self.base_path}')
        documents = []
        c = self.components
        file_locations = c.globber.glob(self.base_path)
        for file_location in file_locations:
            try:
                if dry_run:
                    print(f'process index: {repr(file_location.path)}')
                    continue
                screening_result = c.screener.screen([file_location])[0]
                if screening_result.status == ScreeningStatus.APPROVED:
                    assert screening_result.file_stamp is not None
                    file_stamp = screening_result.file_stamp
                    indexed_document = c.indexer.index(file_location, file_stamp)
                    c.upserter.upsert(indexed_document)
                    print(f'success index: {repr(file_location.path)}, id: {indexed_document.file_id}')
                    documents.append(indexed_document)
                else:
                    print(f'skipped index: {repr(file_location.path)}, reason: {screening_result.reason}')
            except Exception as e:
                print(f'skipped index: {repr(file_location.path)}, reason: {e}')
        pass

class App():
    Config = AppConfig
    _COMPONENT_CLASS_MAP = {
        'PathspecGlobberConfig': pkms.component.globber.PathspecGlobber,
        'SimpleScreenerConfig': pkms.component.screener.SimpleScreener,
        'Sqlite3UpserterConfig': pkms.component.upserter.Sqlite3Upserter,
        'HtmlIndexerConfig': pkms.component.indexer.HtmlIndexer,
        'MarkdownIndexerConfig': pkms.component.indexer.MarkdownIndexer,
        'OdtIndexerConfig': pkms.component.indexer.OdtIndexer,
        'UriResolverConfig': pkms.component.resolver.UriResolver,
        'Sqlite3SearcherConfig': pkms.component.searcher.Sqlite3Searcher,
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
        # print(f'components.keys()={self.components.keys()}')

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
                # print(f'name={name}, config={component_config}')
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
        


        
from pydantic import TypeAdapter

def main(argv):
    args = parse_args(argv)
    logging.debug(f'load config, args.config_path={args.config_path}')
    config_json = {}
    with open(args.config_path, 'r') as f:
        config_json = json.load(f)
    config = AppConfig(**config_json)
    app = App(config=config)
    app.run(dry_run=args.dry_run)
    return 0


if __name__ == '__main__':
    logging.remove()
    logging.add(sys.stderr, level="DEBUG")
    argv = sys.argv
    code = main(argv)
    sys.exit(code)

# from pkms.component.globber import GlobberConfigUnion
# TypeAdapter(GlobberConfigUnion).validate_python({
#     "type": "PathspecGlobberConfig",
#     "patterns": ["*.*"]
# })