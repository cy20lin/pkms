from typing import Optional, Union, Dict, List, Literal
import pathspec
import logging
import pathlib
from pkms.core.model import FileLocation
from pkms.core.component.globber import (
    Globber,
    GlobberConfig,
    GlobberRuntime,
)
import os

def _try_append_slash(path:str):
    return path+'/' if not path.endswith('/') else path

class PathspecGlobberConfig(GlobberConfig):
    type: Literal['PathspecGlobberConfig'] = 'PathspecGlobberConfig'

class PathspecGlobberRuntime(GlobberRuntime):
    pass

class PathspecGlobber(Globber):
    Config = PathspecGlobberConfig
    Runtime = PathspecGlobberRuntime
    type: str = Literal['hello']

    def __init__(self, config:PathspecGlobberConfig, runtime:PathspecGlobberRuntime=None):
        super().__init__(config=config, runtime=runtime)
        self._pathspec = pathspec.PathSpec.from_lines(pattern_factory='gitwildmatch', lines=config.patterns)
    
    def glob(self, base_location:FileLocation) -> FileLocation:
        result = []
        if base_location.scheme == 'file' and base_location.authority == '':
            path_convention = 'windows' if os.name == 'nt' else 'posix'
            base_path = base_location.to_filesystem_path(path_convention=path_convention)
            base_path_ = pathlib.Path(base_path, '')
            base_path_str = _try_append_slash(base_path_.absolute().as_posix())
            sub_paths = self._pathspec.match_tree_files(root=base_path_str, negate=self.config.negate)
            result = [ 
                FileLocation.from_filesystem_path(sub_path, base_path=base_path_str, path_convention=path_convention)
                for sub_path in sub_paths 
            ]
        else:
            raise RuntimeError(
                f'Unsupported scheme={base_location.scheme}'
                f' and authority={base_location.authority!r}'
                f' with base_location={base_location}'
            )
        return result
    
    def match(self, file_location: FileLocation) -> bool:
        result = False
        if file_location.scheme == 'file' and file_location.authority == '':
            path_convention = 'windows' if os.name == 'nt' else 'posix'
            file_path = file_location.to_filesystem_path(path_convention=path_convention)
            result = self._pathspec.match_file(file_path)
        return result







