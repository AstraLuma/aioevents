import asyncio
import gc
import logging


# # # IMPORTANT # # #
# Because aioevents swallows exceptions, asserts cannot go in handlers. Data
# must be martialed out and tested in the main body.


async def test_trigger(Spam, sync_handler):
    """
    Test basic trigger calls.

    Makes sure that each handler is called once, and only after the current
    task blocks.
    """
    spam = Spam()

    spam.egged.handler(sync_handler)
    Spam.egged.handler(sync_handler)

    spam.egged()

    assert sync_handler.calls == []

    await asyncio.sleep(0)  # Yield to everything

    assert sync_handler.calls == [((), {}), ((), {})]


async def test_trigger_pargs(Spam, sync_handler):
    """
    Test that positional arguments get passed through
    """
    spam = Spam()

    spam.egged.handler(sync_handler)
    Spam.egged.handler(sync_handler)

    spam.egged(42, "foobar")
    await asyncio.sleep(0)  # Yield to everything

    assert sync_handler.calls == [
        ((42, "foobar"), {}),
        ((42, "foobar"), {}),
    ]


async def test_trigger_kwargs(Spam, sync_handler):
    """
    Test that keyword arguments get passed through
    """
    spam = Spam()

    spam.egged.handler(sync_handler)
    Spam.egged.handler(sync_handler)

    spam.egged(foo='bar')
    await asyncio.sleep(0)  # Yield to everything

    assert sync_handler.calls == [
        ((), {'foo': 'bar'}),
        ((), {'foo': 'bar'}),
    ]


def test_trigger_noloop(event_loop, Spam, sync_handler):
    """
    Test that everything works when there's no loop
    """
    spam = Spam()

    spam.egged.handler(sync_handler)
    Spam.egged.handler(sync_handler)

    spam.egged(42, foo='bar')

    event_loop.run_until_complete(asyncio.sleep(0))

    assert sync_handler.calls == [
        ((42,), {'foo': 'bar'}),
        ((42,), {'foo': 'bar'}),
    ]


async def test_trigger_async(Spam, async_handler):
    """
    Test that everything works when using async handlers
    """
    spam = Spam()

    spam.egged.handler(async_handler)
    Spam.egged.handler(async_handler)

    spam.egged(42, foo='bar')
    await asyncio.sleep(0)  # Yield to everything

    assert async_handler.calls == [
        ((42,), {'foo': 'bar'}),
        ((42,), {'foo': 'bar'}),
    ]


async def test_handler_gc(Spam, sync_handler, async_handler):
    """
    Test that between handler task creation and loop execution,
    handler tasks don't get gc'd.

    This is because oprhaned Tasks may be cancelled and cleaned up. See
    :func:`asyncio.create_task`.
    """
    Spam.egged.handler(async_handler)
    Spam.egged.handler(sync_handler)

    Spam.egged(42, foo='bar')  # This creates any tasks/threads/etc to call handlers

    gc.collect()  # This will hopefully clean up any orphans
    await asyncio.sleep(0)  # Yield to the loop, letting things execute

    assert len(async_handler.calls) == 1
    assert len(sync_handler.calls) == 1


async def test_trigger_exception(Spam, caplog):
    """
    Test that exceptions produce log events
    """
    @Spam.egged.handler
    def on_egged(foo):
        raise Exception("Boo!")

    with caplog.at_level(logging.DEBUG):
        Spam.egged(foo='bar')
        await asyncio.sleep(0)  # Yield to everything

    assert any(r.name in ('aioevents',)
               and r.levelname == 'ERROR' for r in caplog.records), caplog.records


async def test_trigger_exception_async(Spam, caplog):
    """
    Test that exceptions produce log events
    """
    @Spam.egged.handler
    async def on_egged(foo):
        raise Exception("Boo!")

    with caplog.at_level(logging.DEBUG):
        Spam.egged(foo='bar')
        await asyncio.sleep(0)  # Yield to everything

    assert any(r.name in ('aioevents',)
               and r.levelname == 'ERROR' for r in caplog.records), caplog.records


def test_trigger_exception_noloop(event_loop, Spam, caplog):
    """
    Test that exceptions produce log events (outside of a loop)
    """
    @Spam.egged.handler
    def on_egged(foo):
        raise Exception("Boo!")

    with caplog.at_level(logging.DEBUG):
        Spam.egged(foo='bar')
        event_loop.run_until_complete(asyncio.sleep(0))

    assert any(r.name in ('aioevents',)
               and r.levelname == 'ERROR' for r in caplog.records), caplog.records


async def test_weakref(Spam):
    """
    Test that weak handlers are cleaned up properly.
    """
    calls = 0

    def sync_handler():
        nonlocal calls
        calls += 1

    async def async_handler():
        nonlocal calls
        calls += 1

    Spam.egged.handler(sync_handler, weak=True)
    Spam.egged.handler(async_handler, weak=True)

    del sync_handler, async_handler
    gc.collect()

    Spam.egged()
    await asyncio.sleep(0)

    assert calls == 0


async def test_methods(Spam):
    """
    Test that bound method handlers work correctly.
    """
    calls = 0

    class Harry:
        def sync_handler(self):
            nonlocal calls
            calls += 1

        async def async_handler(self):
            nonlocal calls
            calls += 1

    h = Harry()
    Spam.egged.handler(h.sync_handler)
    Spam.egged.handler(h.async_handler)

    gc.collect()

    Spam.egged()
    await asyncio.sleep(0)

    assert calls == 2


async def test_methods(Spam):
    """
    Test that bound method handlers and weakrref work correctly.
    """
    calls = 0

    class Harry:
        def sync_handler(self):
            nonlocal calls
            calls += 1

        async def async_handler(self):
            nonlocal calls
            calls += 1

    h = Harry()
    Spam.egged.handler(h.sync_handler, weak=True)
    Spam.egged.handler(h.async_handler, weak=True)

    del h
    gc.collect()

    Spam.egged()
    await asyncio.sleep(0)

    assert calls == 0
