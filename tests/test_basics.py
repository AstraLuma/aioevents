import asyncio
import logging


async def test_trigger(Spam, mocker):
    """
    Test basic trigger calls
    """
    spam = Spam()

    inst_handler = mocker.stub('inst_handler')
    cls_handler = mocker.stub('cls_handler')

    spam.egged.handler(inst_handler)
    Spam.egged.handler(cls_handler)

    spam.egged()
    await asyncio.sleep(0)  # Yield to everything

    assert inst_handler.call_count == 1
    assert cls_handler.call_count == 1


async def test_trigger_pargs(Spam, mocker):
    """
    Test that positional arguments get passed through
    """
    spam = Spam()

    inst_handler = mocker.stub('inst_handler')
    cls_handler = mocker.stub('cls_handler')

    spam.egged.handler(inst_handler)
    Spam.egged.handler(cls_handler)

    spam.egged(42, "foobar")
    await asyncio.sleep(0)  # Yield to everything

    assert inst_handler.call_args == ((42, "foobar"), {})
    assert cls_handler.call_args == ((42, "foobar"), {})


async def test_trigger_kwargs(Spam, mocker):
    """
    Test that keyword arguments get passed through
    """
    spam = Spam()

    inst_handler = mocker.stub('inst_handler')
    cls_handler = mocker.stub('cls_handler')

    spam.egged.handler(inst_handler)
    Spam.egged.handler(cls_handler)

    spam.egged(foo='bar')
    await asyncio.sleep(0)  # Yield to everything

    assert inst_handler.call_args == ((), {'foo': 'bar'})
    assert cls_handler.call_args == ((), {'foo': 'bar'})


def test_trigger_noloop(event_loop, Spam, mocker):
    """
    Test that everything works when there's no loop
    """
    spam = Spam()

    inst_handler = mocker.stub('inst_handler')
    cls_handler = mocker.stub('cls_handler')

    spam.egged.handler(inst_handler)
    Spam.egged.handler(cls_handler)

    spam.egged(42, foo='bar')

    event_loop.run_until_complete(asyncio.sleep(0))

    assert inst_handler.call_args == ((42,), {'foo': 'bar'})
    assert cls_handler.call_args == ((42,), {'foo': 'bar'})


async def test_trigger_exception(Spam, caplog):
    """
    Test that exceptions produce log events
    """
    @Spam.egged.handler
    def on_egged(foo):
        raise Exception("Boo!")

    with caplog.at_level(logging.DEBUG, 'aioevents'):
        Spam.egged(foo='bar')
        await asyncio.sleep(0)  # Yield to everything

    assert any(r.name in ('aioevents', 'asyncio')
               and r.levelname == 'ERROR' for r in caplog.records)


def test_trigger_exception_noloop(event_loop, Spam, caplog):
    """
    Test that exceptions produce log events (outside of a loop)
    """
    @Spam.egged.handler
    def on_egged(foo):
        raise Exception("Boo!")

    with caplog.at_level(logging.DEBUG, 'aioevents'):
        Spam.egged(foo='bar')
        event_loop.run_until_complete(asyncio.sleep(0))

    assert any(r.name in ('aioevents', 'asyncio')
               and r.levelname == 'ERROR' for r in caplog.records)
