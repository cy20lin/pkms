from abc import ABC, abstractmethod
from ..model import FileLocation
from ..model import GlobberConfig

class Globber(ABC):

    def __init__(self, config: GlobberConfig):
        self.config = config

    @abstractmethod
    def glob(self, base_path) -> list[FileLocation]:
        ...