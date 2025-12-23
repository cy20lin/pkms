from abc import ABC, abstractmethod
from ..model import FileDescriptor

class Globber(ABC):

    @abstractmethod
    def glob(self) -> list[FileDescriptor]:
        ...