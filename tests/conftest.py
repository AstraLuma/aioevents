import pytest

import aioevents


@pytest.fixture
def Spam():
    class Spam:
        egged = aioevents.Event("The spam has been egged")

    return Spam
