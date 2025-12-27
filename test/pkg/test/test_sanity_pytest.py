# test_math.py

import pytest

def add(x, y):
    return x + y

def subtract(x, y):
    return x - y

# Basic tests
def test_add():
    assert add(2, 3) == 5
    assert add(-1, 1) == 0

def test_subtract():
    assert subtract(5, 3) == 2
    assert subtract(0, 4) == -4

# Using pytest parametrize for multiple cases
@pytest.mark.parametrize("x, y, expected", [
    (2, 3, 5),
    (-1, -1, -2),
    (100, 200, 300),
])
def test_add_param(x, y, expected):
    assert add(x, y) == expected


if __name__ == '__main__':
    # pytest.main(["-v", "--tb=short", __file__])
    pytest.main([__file__])