from ._Walker import Walker
from ._ResolverPolicy import ResolverPolicy
from ..utility._BracesRefResolver import BracesRefResolver
import copy

class ConfigResolver:
    def __init__(self):
        self.policy = ResolverPolicy()
        self.walker = Walker(policy=self.policy)

    def resolve(self, source, context: dict):
        context = copy(context)
        return self.walker.walk(root=source, context=context)