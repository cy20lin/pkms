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
    
    def glob(self, base_path:str) -> FileLocation:
        base_path_ = pathlib.Path(base_path, '')
        base_path_str = _try_append_slash(base_path_.absolute().as_posix())
        sub_paths = self._pathspec.match_tree_files(root=base_path_str, negate=self.config.negate)
        path_convention = 'windows' if isinstance(base_path_, pathlib.WindowsPath) else 'posix'
        result = [ 
            FileLocation.from_filesystem_path(sub_path, base_path=base_path_str, path_convention=path_convention)
            for sub_path in sub_paths 
        ]
        return result






