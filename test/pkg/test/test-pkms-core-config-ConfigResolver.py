from pkms.core.config import Walker, ResolverPolicy, ConfigResolver
from loguru import logger

def test_config_resolver():
    resolver = ConfigResolver()
    c = {'app': {"x": 'hello world'}}
    x = '${app.x}'
    y = resolver.resolve(x, c)
    logger.info(f'{y!r}')

def test_config_resolver():
    resolver = ConfigResolver()
    c = {
        'app': {
            'two': 2,
            'hello': 'world',
        }
    }
    x = {
        'o': {
            'a': 12,
        },
        'x': 1,
        'y': "${root.x}",
        'two': "${raw.app.two}",
        'app': "${app}",
        'world': "${root.app.hello}",
        'two': "${raw.app.two}",
        'rawtwo': "${raw.root.two}",
    }
    y = resolver.resolve(x, c)
    logger.debug(f'{y!r}')
    assert isinstance(y, dict)
    assert y['o'] == {'a': 12}
    assert y['x'] == 1
    assert y['y'] == y['x']
    assert y['two'] == c['app']['two']
    assert y['app'] == c['app']
    assert y['world'] == c['app']['hello']
    assert y['rawtwo'] == x['two']

if __name__ == '__main__':
    test_config_resolver()