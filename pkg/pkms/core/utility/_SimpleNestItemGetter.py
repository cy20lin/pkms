from ._NestItemGetter import NestItemGetter
from typing import Iterable,Any,Hashable

class SimpleNestItemGetter(NestItemGetter):
    
    def get(self, root: Any, keys: list[Any]) -> Any:
        """
        Walk ``root`` by performing ``root[key]`` for every ``key`` in *keys*.
        ``key`` may be a string (dictionary key) or an int (list/tuple index).

        Raises:
            KeyError / IndexError / TypeError – if a key cannot be satisfied.
            ValueError – if an integer index is out of the configured safe range.
        """
        target = root
        for key in keys:
            try:
                target = target[key]
            except Exception as e:
                # Add context to the error – it is extremely helpful when the
                # format string is long.
                raise type(e)(f"Failed to resolve key {key!r} on {target!r}: {e}") from e
        return target

    # def set(self, root: Any, keys: list[Any], value: Any) -> Any:
    #     target = root
    #     for key in keys:
    #         try:
    #             target = target[key]
    #         except Exception as e:
    #             # Add context to the error – it is extremely helpful when the
    #             # format string is long.
    #             raise type(e)(f"Failed to resolve key {key!r} on {target!r}: {e}") from e
    #     return target