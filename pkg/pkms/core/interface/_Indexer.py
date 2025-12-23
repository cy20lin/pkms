from abc import ABC, abstractmethod
from ..model import FileDescriptor, IndexedDocument

class Indexer(ABC):

    @abstractmethod
    def index(self, file: FileDescriptor) -> IndexedDocument:
        ...
