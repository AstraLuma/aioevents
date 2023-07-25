"""
Test how events ducktype
"""
import inspect

import pytest


def test_descriptor(Spam):
    """
    Test that events show up as data descriptors.

    This is mostly so that doc tools don't mix events in with methods.
    """
    assert inspect.isdatadescriptor(Spam.egged)


def test_docstrings(Spam):
    """
    Test that the user-given docstring actually gets picked up.
    """
    assert inspect.getdoc(Spam.egged)
    assert inspect.getdoc(Spam().egged)
    assert inspect.getdoc(Spam.egged) == inspect.getdoc(Spam().egged)


def test_name(Spam):
    """
    Test name attrs
    """
    # TODO: Are there standard library ways to pull this info?
    assert Spam.egged.__name__ == 'egged'
    assert Spam.egged.__qualname__.endswith('Spam.egged')
    assert Spam().egged.__name__ == 'egged'
    assert Spam().egged.__qualname__.endswith('Spam.egged')


def test_cant_set(Spam):
    """
    Test that we can't actually set an event
    """
    with pytest.raises(AttributeError):
        Spam().egged = 42
