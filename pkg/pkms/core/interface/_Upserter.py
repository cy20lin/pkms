from abc import ABC, abstractmethod
from ..model import IndexedDocument, UpserterConfig

class Upserter(ABC):
    Config: type[UpserterConfig] = UpserterConfig

    def __init__(self, config: UpserterConfig):
        self.config = config

    @abstractmethod
    def upsert(self, doc: IndexedDocument) -> None:
        ...
