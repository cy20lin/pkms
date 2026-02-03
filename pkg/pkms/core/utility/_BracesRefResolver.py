from typing import Any
from ._SafeNestFormatter import (
    get_nest_item,
    SafeNestFormatter
)
from ._DollarBracesRefResolver import (
    DollarBracesRefResolver
)
import re

class BracesRefResolver:

    PATTERN = re.compile(r'^(?P<dollar>\$+)(?P<open>\{+)(?P<ref>[\w.]+)(?P<close>\}+)$')
    def __init__(self):
        self.fmt_braces_formatter = SafeNestFormatter()
        self.dollar_braces_resolver = DollarBracesRefResolver()

    def resolve(self, target:Any, root:dict) -> Any:
        return self.try_resolve(target, root)[1]

    def try_resolve(self, target:Any, root:dict) -> Any:
        is_resolved, result =self.dollar_braces_resolver.try_resolve(target, root)
        if is_resolved:
            pass
        elif isinstance(target, str):
            result = self.fmt_braces_formatter.format(target, root=root)
            is_resolved=True
        else:
            result = target
            is_resolved=False
        return is_resolved, result
