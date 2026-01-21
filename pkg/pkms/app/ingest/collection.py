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


from pkms.component.globber import GlobberConfigUnionRef
from pkms.component.screener import ScreenerConfigUnionRef
from pkms.component.indexer import IndexerConfigUnionRef
from pkms.component.upserter import UpserterConfigUnionRef
from pkms.component.resolver import ResolverConfigUnionRef
from pkms.component.searcher import SearcherConfigUnionRef
from pkms.core.component import Component
from pydantic import BaseModel, ConfigDict, Field


from pkms.component.indexer import IndexerConfigUnion

class ComponentsConfig(BaseModel):
    model_config = ConfigDict(extra="allow")
    globber: GlobberConfigUnionRef
    screener: ScreenerConfigUnionRef
    indexer: IndexerConfigUnionRef
    upserter: UpserterConfigUnionRef
    searcher: SearcherConfigUnionRef
    resolver: ResolverConfigUnionRef


from typing import Optional, Dict, List, Literal
from pydantic import BaseModel, ConfigDict, Field

class CollectionConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str
    base_path: str
    description: Optional[str] = None
    components: ComponentsConfig 

class CollectionRuntime():
    pass

from pkms.core.model import ScreeningStatus

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