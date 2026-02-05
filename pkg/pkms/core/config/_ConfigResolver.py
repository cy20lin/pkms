from ._Walker import Walker
from ._ResolverPolicy import ResolverPolicy
from ..utility._BracesRefResolver import BracesRefResolver

class ConfigResolver:
    def __init__(self):
        self.policy = ResolverPolicy()
        self.walker = Walker(policy=self.policy)

    def resolve(self, root, context: dict):
        context['raw'] = context.copy()
        context['raw']['root'] = root
        return self.walker.walk(base=root, context=context, base_keys=('root',))