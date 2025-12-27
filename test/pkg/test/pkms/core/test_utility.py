import pytest

from pkms.core.utility import (
    parse_file_name
)

def test_parse_file_name():
    parsed = parse_file_name("0000-00-00-deadbeef Hello World.en.md")
    assert parsed['name'] == "0000-00-00-deadbeef Hello World.en.md"
    assert parsed['id'] == "0000-00-00-deadbeef.en.md"
    assert parsed['id_prefix'] == "0000-00-00-deadbeef"
    assert parsed['importance'] == 0
    assert parsed['extension'] == '.en.md'
    assert parsed['title'] == 'Hello World'
    assert parsed['context'] == None

    parsed = parse_file_name("/path/to/0000-00-00-deadbeef !!! Hello World.en.md")
    assert parsed['name'] == "0000-00-00-deadbeef !!! Hello World.en.md"
    assert parsed['id'] == "0000-00-00-deadbeef.en.md"
    assert parsed['id_prefix'] == "0000-00-00-deadbeef"
    assert parsed['importance'] == 3
    assert parsed['extension'] == '.en.md'
    assert parsed['title'] == 'Hello World'
    assert parsed['context'] == None

if __name__ == '__main__':
    pytest.main([__file__])