from ..utility._NestItemGetter import NestItemGetter
from ._ResolverContext import ResolverContext
from ..utility._SimpleNestItemGetter import SimpleNestItemGetter

class ResolverContextNestItemGetter(NestItemGetter):
    def __init__(self, enable_fallback=False):
        self.getter = SimpleNestItemGetter()
        self.enable_fallback = enable_fallback
    
    def _find_frame(self, target: ResolverContext, keys: tuple[str|int]):
        if len(target.frames_base) > len(keys) or any(frame_key != key for frame_key,key in zip(target.frames_base, keys)):
            result = -1
        else:
            result = 0
            for frame,key in zip(target.frames[1:], keys):
                if frame.key == key:
                    result += 1
        return result

    def get(self, target: ResolverContext, keys: tuple[str|int]):
        i = self._find_frame(target, keys)
        result = None
        if i >= 0:
            data = target.frames[i].resolved_children
            data_keys = keys[len(target.frames_base)+i:]
            if self.enable_fallback:
                has_result = False
                try:
                    result = self.getter.get(data, data_keys)
                    has_result = True
                except Exception as e:
                    pass
                if not has_result:
                    result = self.getter.get(target.external, keys)
            else:
                result = self.getter.get(data, data_keys)
        else:
            result = self.getter.get(target.external, keys)
        return result
