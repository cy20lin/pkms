from ..component import ComponentConfigUnion
from ..core.component import Component

ComponentRegistryConfig = dict[str,ComponentConfigUnion]
ComponentRegistry = dict[str,Component]

__all__ = [
    'ComponentRegistry'
]