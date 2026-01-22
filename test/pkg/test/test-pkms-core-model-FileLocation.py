# test_file_location.py

import pytest
from pkms.core.model import FileLocation

def test_from_uri_default_scheme():
    location = FileLocation.from_uri('file:///example/path/to/file')
    assert location.scheme == 'file'
    assert location.authority == ''
    assert location.base_path == ''
    assert location.sub_path == '/example/path/to/file'

def test_from_uri_custom_base_path():
    location = FileLocation.from_uri('file:///example/path/to/file', base_path='/custom/base')
    assert location.scheme == 'file'
    assert location.authority == ''
    assert location.base_path == '/custom/base'
    assert location.sub_path == '/example/path/to/file'

def test_from_uri_relative_path():
    location = FileLocation.from_uri('file://host/path/to/file', base_path='/base/path')
    assert location.scheme == 'file'
    assert location.authority == 'host'
    assert location.base_path == '/base/path'
    assert location.sub_path == '/path/to/file'

def test_from_uri_authority():
    location = FileLocation.from_uri('file://user@host/path/to/file')
    assert location.authority == 'user@host'
    assert location.base_path == ''
    assert location.sub_path == '/path/to/file'

def test_from_uri_uri_with_trailing_slash():
    location = FileLocation.from_uri('file:///example/path/to/file/')
    assert location.sub_path == '/example/path/to/file/'

def test_path_property():
    location = FileLocation(scheme='file', authority='', base_path='/base', sub_path='sub')
    assert location.path == '/base/sub'

def test_path_property_no_base_or_sub():
    location = FileLocation(scheme='file', authority='', base_path='', sub_path='')
    assert location.path == '/'

def test_uri_property():
    location = FileLocation(scheme='file', authority='', base_path='/base', sub_path='sub')
    assert location.uri.startswith('file:///base/sub')

def test_from_windows_uri():
    # On Windows, this might raise a ValueError, which we expect to be handled
    location = FileLocation.from_uri('file:///d:/example/path', base_path='/c:/')
    assert location.sub_path.startswith('/d:')
    assert location.sub_path.endswith('example/path')

def test_fs_path_from_windows_file_uri():
    location = FileLocation.from_uri('file:///d:/example/path', base_path='/c:/')
    assert location.fs_path == 'd:/example/path'

def test_uri_property_absolute_path():
    location = FileLocation(scheme='file', authority='', base_path='/absolute/path', sub_path='sub')
    uri = location.uri
    assert uri.startswith('file:///absolute/path/sub')

def test_invalid_uri():
    with pytest.raises(ValueError):
        FileLocation.from_uri('invalid_uri')

# Additional tests can be added to cover more edge cases and scenarios as needed.