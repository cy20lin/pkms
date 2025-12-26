from pkms.core.interface._Globber import Globber
import pathspec
import logging
import pathlib
from pkms.core.model import FileLocation
from pkms.core.model import GlobberConfig
import os

def _try_append_slash(path:str):
    return path+'/' if not path.endswith('/') else path

class PathspecGlobber(Globber):
    def __init__(self, config:GlobberConfig):
        super().__init__(config=config)
        self._pathspec = pathspec.PathSpec.from_lines(pattern_factory='gitignore', lines=config.patterns)
    
    def glob(self, base_path:str) -> FileLocation:
        base_path_ = pathlib.Path(base_path, '')
        base_path_posix = _try_append_slash(base_path_.absolute().as_posix())
        sub_paths = self._pathspec.match_tree_files(root=base_path_posix, negate=self.config.negate)
        result = [ 
            FileLocation(
                scheme='file',
                authority='',
                base_path=base_path_posix,
                sub_path=sub_path.replace('\\', '/')
            ) 
            for sub_path in sub_paths 
        ]
        return result






