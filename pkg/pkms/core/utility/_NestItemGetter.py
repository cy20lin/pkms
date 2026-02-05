from abc import ABC, abstractmethod
from typing import Iterable,Any,Hashable

class NestItemGetter(ABC):

    @abstractmethod
    def get(self, root, keys: Iterable[Hashable]):
        pass
