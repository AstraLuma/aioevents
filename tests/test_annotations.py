"""
Test type annotations and generic stuff.
"""
from typing import Callable, Self

import pytest

from aioevents import Event


@pytest.mark.mypy_testing
def test_basics():
    """
    Just test the basic use case works
    """
    class Duck:
        quack = Event[Callable[[Self], None]]("the noise ducks make")

    daffy = Duck()

    @Duck.quack.handler
    def on_quack(sender: Duck):
        pass

    @daffy.quack.handler
    def on_some_quack(sender: Duck):
        pass
