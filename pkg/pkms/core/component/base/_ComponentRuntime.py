from abc import ABC

class ComponentRuntime(ABC):
    """
    Runtime holds execution-scoped external resources.

    Examples:
    - DB connections / pools
    - thread-local caches
    - shared registries
    """

    def shutdown(self) -> None:
        """
        Optional lifecycle hook.
        Application MAY call this.
        """
        pass
