import pytest

import aioevents


@pytest.fixture
def Spam():
    class Spam:
        egged = aioevents.Event("The spam has been egged")

    return Spam


# The handler fixtures should be mocks, but the standard mocking libraries seem
# to disagree with type detection.

@pytest.fixture
def SyncHandler():
    def factory():
        def handler(*pargs, **kwargs):
            handler.calls.append((pargs, kwargs))

        handler.calls = []
        return handler
    return factory


@pytest.fixture
def sync_handler(SyncHandler):
    return SyncHandler()


@pytest.fixture
def AsyncHandler():
    def factory():
        async def handler(*pargs, **kwargs):
            handler.calls.append((pargs, kwargs))

        handler.calls = []
        return handler
    return factory


@pytest.fixture
def async_handler(AsyncHandler):
    return AsyncHandler()
