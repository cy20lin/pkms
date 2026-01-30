from pkms.core.utility._env import (
    SimpleNameMap,
    parse_env
)

# Tests for SimpleNameMap
def test_simple_name_map_no_transform():
    name_map = SimpleNameMap()
    assert name_map("TEST") == "TEST"

def test_simple_name_map_remove_prefix():
    name_map = SimpleNameMap(remove_prefix='PREFIX_')
    assert name_map("PREFIX_TEST") == "TEST"
    assert name_map("NOT_PREFIXED") == "NOT_PREFIXED"  # No change when prefix is not there

def test_simple_name_map_swap_case():
    name_map = SimpleNameMap(swap_case=True)
    assert name_map("TEST") == "test"
    
def test_simple_name_map_remove_prefix_and_swap_case():
    name_map = SimpleNameMap(remove_prefix='PREFIX_', swap_case=True)
    assert name_map("PREFIX_TEST") == "test"
    assert name_map("PREFIX_test") == "TEST"
    assert name_map("NO_PREFIX") == "no_prefix"  # both transformations applied

# Tests for parse_env
def test_parse_env_no_transformation():
    environ = {'VAR1': 'value1', 'VAR2': 'value2'}
    var_names = ['VAR1', 'VAR2']
    expected = {'VAR1': 'value1', 'VAR2': 'value2'}
    result = parse_env(environ, var_names)
    assert result == expected

def test_parse_env_with_name_map_removing_prefix():
    environ = {'PREFIX_VAR1': 'value1', 'VAR2': 'value2'}
    var_names = ['PREFIX_VAR1', 'VAR2']
    name_map = SimpleNameMap(remove_prefix="PREFIX_")
    expected = {'VAR1': 'value1', 'VAR2': 'value2'}
    result = parse_env(environ, var_names, name_map)
    assert result == expected

def test_parse_env_with_name_map_swap_case():
    environ = {'var1': 'value1', 'VAR2': 'value2'}
    var_names = ['var1', 'VAR2']
    name_map = SimpleNameMap(swap_case=True)
    expected = {'VAR1': 'value1', 'var2': 'value2'}
    result = parse_env(environ, var_names, name_map)
    assert result == expected

def test_parse_env_with_combined_name_map():
    environ = {'PREFIX_var1': 'value1', 'VAR2': 'value2'}
    var_names = ['PREFIX_var1', 'VAR2']
    name_map = SimpleNameMap(remove_prefix="PREFIX_", swap_case=True)
    expected = {'VAR1': 'value1', 'var2': 'value2'}
    result = parse_env(environ, var_names, name_map)
    assert result == expected

def test_parse_env_var_not_present():
    environ = {'VAR1': 'value1'}
    var_names = ['VAR1', 'VAR2']
    expected = {'VAR1': 'value1', 'VAR2': None}  # VAR2 is not in environ
    result = parse_env(environ, var_names)
    assert result == expected