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
