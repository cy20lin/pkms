from abc import ABC, abstractmethod
from ..model import IndexedDocument

class Upserter(ABC):

    @abstractmethod
    def upsert(self, doc: IndexedDocument) -> None:
        ...
