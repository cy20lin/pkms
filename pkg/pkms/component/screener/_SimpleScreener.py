from typing import Iterable, List, Literal, Optional
from pkms.core.component.screener import (
    Screener,
    ScreenerConfig,
    ScreenerRuntime
)
import datetime
import pathspec
import logging
import pathlib
import os
from pkms.core.model import (
    FileLocation,
    ScreenCandidate,
    ScreeningResult,
    FileStamp,
    ScreeningStatus,
)
from pkms.core.component.screener import (
    Screener,
    ScreenerConfig,
    ScreenerRuntime,
)
from pkms.core.utility import (
    parse_file_name,
    get_file_hash_sha256,
)

def _try_append_slash(path:str):
    return path+'/' if not path.endswith('/') else path

class SimpleScreenerConfig(ScreenerConfig):
    type: Literal['SimpleScreenerConfig'] = 'SimpleScreenerConfig'

class SimpleScreenerRuntime(ScreenerRuntime):
    ...

class SimpleScreener(Screener):
    Config = SimpleScreenerConfig
    Runtime = SimpleScreenerRuntime

    def __init__(self, config:SimpleScreenerConfig, runtime: Optional[SimpleScreenerRuntime]= None):
        super().__init__(config=config, runtime=runtime)
    
    def screen(
        self,
        candidates: Iterable[ScreenCandidate],
    ) -> List[ScreeningResult]:
        """
        Screen candidate files.

        - Must NOT perform indexing
        - Must NOT perform database writes
        - Must return explicit screening decisions

        :param candidates: iterable of ScreenCandidate
        :return: list of ScreeningResult (order-preserving)
        """
        results = []
        path_convention = 'windows' if os.name == 'nt' else 'posix'
        for file_location in candidates:
            file_path = file_location.to_filesystem_path(path_convention=path_convention)
            file_name_parsed = parse_file_name(file_path)
            file_stamp = None
            status = ScreeningStatus.REJECTED
            reason = None
            try:
                ## File name specific
                id = file_name_parsed['id']
                uid = None
                extension = file_name_parsed['extension']
                kind = 'snapshot'
                title = file_name_parsed['title']
                importance = file_name_parsed['importance']
                context = file_name_parsed['context']
                file_path = pathlib.Path(file_path)
                stat = file_path.stat()
                ctime = stat.st_ctime
                mtime = stat.st_mtime
                # atime = stat.st_atime
                created_datetime = datetime.datetime.fromtimestamp(ctime).astimezone().isoformat()
                modified_datetime = datetime.datetime.fromtimestamp(mtime).astimezone().isoformat()
                size = stat.st_size
                hash_sha256 = get_file_hash_sha256(file_path)
                metadata = {}
                file_stamp = FileStamp(
                    id=id,
                    uid=uid,
                    extension=extension,
                    kind=kind,
                    title=title,
                    importance=importance,
                    size=size,
                    created_datetime=created_datetime,
                    modified_datetime=modified_datetime,
                    hash_sha256=hash_sha256,
                    metadata=metadata
                )
                status = ScreeningStatus.APPROVED
            except Exception as e:
                reason = str(e)
            result = ScreeningResult(
                status=status,
                file_location=file_location,
                file_stamp=file_stamp,
                reason=reason,
                diagnostics={}
            )
            results.append(result)
        return results






