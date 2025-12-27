from abc import ABC, abstractmethod
from ..model import FileLocation, IndexedDocument, IndexerConfig

class Indexer(ABC):
    Config: type[IndexerConfig] = IndexerConfig

    def __init__(self, config: IndexerConfig):
        self.config = config

    @abstractmethod
    def index(self, file_location: FileLocation) -> IndexedDocument:
        ...
