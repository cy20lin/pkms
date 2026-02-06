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
from pkms.core.model import FileLocation

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
import os

class Collection():
    Config = CollectionConfig
    Runtime = None
    def __init__(self, config:CollectionConfig, runtime: Optional[CollectionRuntime]=None):
        self.config = config
        self.runtime = runtime
        self.name = config.name
        self.description = config.description
        self.base_path = config.base_path
        path_convention= 'windows' if os.name == 'nt' else 'posix'
        self.base_location = FileLocation.from_filesystem_path(self.base_path, path_convention=path_convention)
        self.components: CollectionComponents 
    
    def ingest(self, dry_run:bool|None=False) -> int:
        count = 0
        print(f'collection: name={self.name}, base_path={self.base_path}')
        c = self.components
        path_convention= 'windows' if os.name == 'nt' else 'posix'
        base_location = FileLocation.from_filesystem_path(self.base_path, path_convention=path_convention)
        file_locations = c.globber.glob(base_location)
        for file_location in file_locations:
            file_path = file_location.to_filesystem_path(path_convention=path_convention)
            try:
                if dry_run:
                    print(f'process index: {repr(file_path)}')
                    continue
                screening_result = c.screener.screen([file_location])[0]
                if screening_result.status == ScreeningStatus.APPROVED:
                    assert screening_result.file_stamp is not None
                    file_stamp = screening_result.file_stamp
                    indexed_document = c.indexer.index(file_location, file_stamp)
                    c.upserter.upsert(indexed_document)
                    print(f'success index: {repr(file_path)}, id: {indexed_document.file_id}')
                    count += 1
                else:
                    print(f'skipped index: {repr(file_path)}, reason: {screening_result.reason}')
            except Exception as e:
                print(f'skipped index: {repr(file_path)}, reason: {e}')
        return count

    def ingest_file(self, file_location:FileLocation, dry_run:bool|None=False) -> int:
        count = 0
        print(f'collection: name={self.name}, base_path={self.base_path}')
        c = self.components
        path_convention= 'windows' if os.name == 'nt' else 'posix'
        file_path = file_location.to_filesystem_path(path_convention=path_convention)
        try:
            if dry_run:
                is_matched = c.globber.match(file_location)
                if is_matched:
                    print(f'process index: {repr(file_path)}')
                    count += 1
                else:
                    print(f'skipped index: {repr(file_path)}, reason: not matched with the glob patterns')
            else:
                is_matched = c.globber.match(file_location)
                if is_matched:
                    screening_result = c.screener.screen([file_location])[0]
                    if screening_result.status == ScreeningStatus.APPROVED:
                        assert screening_result.file_stamp is not None
                        file_stamp = screening_result.file_stamp
                        indexed_document = c.indexer.index(file_location, file_stamp)
                        c.upserter.upsert(indexed_document)
                        print(f'success index: {repr(file_path)}, id: {indexed_document.file_id}')
                        count += 1
                    else:
                        print(f'skipped index: {repr(file_path)}, reason: {screening_result.reason}')
                else:
                    print(f'skipped index: {repr(file_path)}, reason: not matched with the glob patterns')
        except Exception as e:
            print(f'skipped index: {repr(file_path)}, reason: {e}')
        return count

    def ingest_files(self, file_locations: list[FileLocation], dry_run:bool|None=False) -> int:
        count = 0
        print(f'collection: name={self.name}, base_path={self.base_path}')
        c = self.components
        path_convention= 'windows' if os.name == 'nt' else 'posix'
        for file_location in file_locations:
            file_path = file_location.to_filesystem_path(path_convention=path_convention)
            try:
                if dry_run:
                    is_matched = c.globber.match(file_location)
                    if is_matched:
                        print(f'process index: {repr(file_path)}')
                        count += 1
                    else:
                        print(f'skipped index: {repr(file_path)}, reason: not matched with the glob patterns')
                else:
                    is_matched = c.globber.match(file_location)
                    if is_matched:
                        print(f'process index: {repr(file_path)}')
                        screening_result = c.screener.screen([file_location])[0]
                        if screening_result.status == ScreeningStatus.APPROVED:
                            assert screening_result.file_stamp is not None
                            file_stamp = screening_result.file_stamp
                            indexed_document = c.indexer.index(file_location, file_stamp)
                            c.upserter.upsert(indexed_document)
                            print(f'success index: {repr(file_path)}, id: {indexed_document.file_id}')
                            count += 1
                        else:
                            print(f'skipped index: {repr(file_path)}, reason: {screening_result.reason}')
                    else:
                        print(f'skipped index: {repr(file_path)}, reason: not matched with the glob patterns')
            except Exception as e:
                print(f'skipped index: {repr(file_path)}, reason: {e}')
        return count