from typing import Any
from ._SafeNestFormatter import (
    get_nest_item,
    SafeNestFormatter
)
from ._DollarBracesRefResolver import (
    DollarBracesRefResolver
)
import re
from ._NestItemGetter import NestItemGetter
from ._SimpleNestItemGetter import SimpleNestItemGetter

class BracesRefResolver:

    PATTERN = re.compile(r'^(?P<dollar>\$+)(?P<open>\{+)(?P<ref>[\w.]+)(?P<close>\}+)$')
    def __init__(self):
        self.fmt_braces_formatter = SafeNestFormatter()
        self.dollar_braces_resolver = DollarBracesRefResolver()
        self.getter = SimpleNestItemGetter()

    def resolve(self, target:Any, root:dict, getter:NestItemGetter) -> Any:
        return self.try_resolve(target, root, getter)[1]

    def try_resolve(self, target:Any, root:dict, getter:NestItemGetter) -> Any:
        is_resolved, result =self.dollar_braces_resolver.try_resolve(target, root, getter=getter)
        if is_resolved:
            pass
        elif isinstance(target, str):
            result = self.fmt_braces_formatter.format(target, root=root, getter=getter)
            is_resolved=True
        else:
            result = target
            is_resolved=False
        return is_resolved, result
