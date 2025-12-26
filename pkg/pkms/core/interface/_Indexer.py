from abc import ABC, abstractmethod
from ..model import FileLocation, IndexedDocument

class Indexer(ABC):

    @abstractmethod
    def index(self, file: FileLocation) -> IndexedDocument:
        ...
