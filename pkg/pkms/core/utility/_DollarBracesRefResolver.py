from typing import Any
from ._SafeNestFormatter import (
    get_nest_item,
    SafeNestFormatter
)
import re
from ._NestItemGetter import NestItemGetter
from ._SimpleNestItemGetter import SimpleNestItemGetter

class DollarBracesRefResolver:

    PATTERN = re.compile(r'^(?P<dollar>\$+)(?P<open>\{+)(?P<ref>[\w.]+)(?P<close>\}+)$')
    def __init__(self):
        self.getter = SimpleNestItemGetter()

    def _get_unescaped_or_ref(self, target):
        unescaped = None
        ref = None
        if isinstance(target, str):
            m = self.PATTERN.match(target)
            if m and len(m.group('open')) == 1 and len(m.group('close')) == 1:
                if len(m.group('dollar')) == 1:
                    ref = m.group('ref')
                else:
                    unescaped = target[1:]
        return unescaped, ref

    def resolve(self, target:Any, root:dict, getter:NestItemGetter|None = None) -> Any:
        return self.try_resolve(target, root, getter)[1]

    def try_resolve(self, target:Any, root:dict, getter: NestItemGetter|None = None) -> Any:
        if getter is None:
            getter = self.getter
        is_resolved = False
        result = target
        if isinstance(target, str):
            unescaped, ref = self._get_unescaped_or_ref(target)
            if unescaped:
                result = unescaped
                is_resolved = True
            elif ref:
                parts = SafeNestFormatter.tokenize(ref)
                result = getter.get(root, parts)
                is_resolved = True
        return is_resolved, result
