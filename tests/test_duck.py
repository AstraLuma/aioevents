"""
Test how events ducktype
"""
import inspect


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
