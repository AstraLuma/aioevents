from __future__ import annotations
from typing import Callable
from aioevents import Event
from typing_extensions import assert_type


def test_duck() -> None:
    class Duck:
        quack = Event['Duck']("the noise ducks make")

    @Duck.quack.handler
    def on_quack(sender: Duck) -> None:
        pass

    assert_type(on_quack, Callable[[Duck], None])
