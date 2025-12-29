from abc import ABC, abstractmethod
from ..model import SearcherConfig, SearchArguments, SearchResult


class Searcher(ABC):
    """
    Abstract base class for all searchers.
    """

    Config: type[SearcherConfig] = SearcherConfig

    def __init__(self, *, config: SearcherConfig):
        self.config = config

    @abstractmethod
    def search(self, args: SearchArguments) -> SearchResult:
        """
        Execute a search query.
        """
        raise NotImplementedError