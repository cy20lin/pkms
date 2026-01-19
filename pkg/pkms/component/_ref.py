from typing import Type, Union

def make_component_ref_factory(config_union_type: Type):
    def _factory(*args, **kwargs):
        if len(kwargs) == 0 and len(args) == 1:
            if isinstance(args[0], (str, config_union_type)):
                return args[0]
            raise ValueError(
                f'Failed to construct from type={type(args[0])}'
            )

        if len(args) == 0:
            return config_union_type(**kwargs)

        raise ValueError(
            f'Failed to construct from args={args}, kwargs={kwargs}'
        )
    return _factory