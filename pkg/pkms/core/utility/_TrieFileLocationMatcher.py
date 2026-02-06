from typing import Iterable,Optional
from ..model import FileLocation
from ._FileLocationMatcher import FileLocationMatcher

# NOTE: this class is reserved for future Trie (prefix-tree) based FileLocationMatcher implementation 
class TrieFileLocationMatcher(FileLocationMatcher):
    def __init__(self, file_locations: Iterable[FileLocation]):
        super().__init__(file_locations=file_locations)

    def reset(self, file_locations: Iterable[FileLocation]):
        # super().do_reset(file_locations=file_locations)
        raise NotImplementedError()

    def find_match_index(self, file_location: FileLocation) -> Optional[int]:
        raise NotImplementedError()

    def find_match(self, file_location: FileLocation) -> Optional[FileLocation]:
        raise NotImplementedError()