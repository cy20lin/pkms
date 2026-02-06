from typing import Iterable,Optional
from abc import ABC,abstractmethod
from ..model import FileLocation

class FileLocationMatcher(ABC):
    def __init__(self, file_locations: Iterable[FileLocation]):
        self.file_locations = list(file_locations)

    def do_reset(self, file_locations: Iterable[FileLocation]):
        self.file_locations = list(file_locations)

    @abstractmethod
    def reset(self, file_locations: Iterable[FileLocation]):
        pass

    @abstractmethod
    def find_match_index(self, file_location: FileLocation) -> int:
        pass

    @abstractmethod
    def find_match(self, file_location: FileLocation) -> Optional[FileLocation]:
        pass