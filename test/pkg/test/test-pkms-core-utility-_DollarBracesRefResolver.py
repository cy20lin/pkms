import pytest
from pkms.core.utility import DollarBracesRefResolver

def test_ObjectDereferencer():
    resolver = DollarBracesRefResolver()
    context = {
        'x': 123,
        'o': {
            'a': 'xxx'
        }
    }
    assert resolver.resolve("${x}", root=context) == 123
    assert resolver.resolve("${o.a}", root=context) == 'xxx'
    assert resolver.resolve("$${o.a}", root=context) == '${o.a}'
    assert resolver.resolve("$$${o.a}", root=context) == '$${o.a}'

    assert resolver.try_resolve("{x}", root=context) == (False,'{x}')
    assert resolver.try_resolve("${x}", root=context) == (True,123)
    assert resolver.try_resolve("${o.a}", root=context) == (True,'xxx')
    assert resolver.try_resolve("$${o.a}", root=context) == (True,'${o.a}')
    assert resolver.try_resolve("$$${o.a}", root=context) == (True,'$${o.a}')