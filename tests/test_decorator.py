import pytest

from flowforgeai import flowforge
from flowforgeai import get_registered_function


def test_decorator():

    @flowforge
    def test_function():
        return "test"

    assert get_registered_function("test_function") == test_function
    assert test_function() == "test"
