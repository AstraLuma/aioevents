"""
This is a sample module to demonstrate how events look in Sphinx.
"""

from aioevents import Event


class Spam:
    """
    This is an example class
    """
    egged = Event("The spam has been egged")
