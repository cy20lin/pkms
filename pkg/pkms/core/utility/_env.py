from typing import Iterable

class SimpleNameMap:
    def __init__(self, /, *, remove_prefix=None, swap_case:bool = False):
        self.remove_prefix = remove_prefix
        self.swap_case = swap_case
    
    def __call__(self, value:str, *args, **kwds):
        if self.remove_prefix and value.startswith(self.remove_prefix):
            value = value[len(self.remove_prefix):]
        if self.swap_case:
            value = value.swapcase()
        return value

def parse_env(environ: dict[str,str], var_names: Iterable[str], name_map=None) -> str|None:
    result = {}
    if name_map is None:
        name_map = lambda x: x
    for var_name in var_names:
        key = name_map(var_name)
        result[key] = environ.get(var_name)
    return result