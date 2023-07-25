"""
Events for asyncio
"""

import asyncio
import inspect
import logging
import types
import weakref
__all__ = 'Event',

LOG = logging.getLogger(__name__)


def _call_handler_sync(func, *pargs, **kwargs):
    """
    Queue a sync function to be called, and wire it into everything
    """
    fut = asyncio.get_event_loop().create_future()

    def _wrapper():
        try:
            func(*pargs, **kwargs)
        except BaseException:
            LOG.exception("Swallowed exception from handler %r", func)
        finally:
            fut.set_result(None)

    asyncio.get_event_loop().call_soon_threadsafe(_wrapper)

    return fut


def _call_handler_async(func, *pargs, **kwargs):
    """
    Queue an async function to be called.
    """
    async def _wrapper():
        try:
            return await func(*pargs, **kwargs)
        except BaseException:
            LOG.exception("Swallowed exception from handler %r", func)

    return asyncio.create_task(_wrapper())


class BoundEvent(set):
    """
    A bound event, produced when :class:`Event` is used as a property on an instance.

    Acts as a set for registered handlers.
    """
    __doc__: str

    def __init__(self, doc: str | None = None, parent: 'Event | None' = None, owner=None):
        if isinstance(doc, str):
            if not doc.startswith("Event:"):
                doc = f"Event: {doc}"  # I'm not completely convinced this is a good idea
            self.__doc__ = doc
        self._pman = parent
        self._owner = None if owner is None else weakref.ref(owner)
        if parent is not None:
            self.__name__ = parent.__name__
            self.__qualname__ = parent.__qualname__

    def trigger(self, *pargs, **kwargs) -> None:
        """
        Schedules the calling of all the registered handlers. Exceptions are
        consumed.

        If the loop is not currently running, queues the callbacks to be called
        after it starts.
        """
        owner = None if self._owner is None else self._owner()
        # Supposedly orphan tasks will be garbage collected, but I can't reproduce.
        for func in [
                f() if isinstance(f, weakref.ReferenceType) else f
                for f in [*(self._pman or set()), *self]
        ]:  # Doubles as a snapshot of the handlers, so they can't be mutated in the loop
            if inspect.iscoroutinefunction(func):
                _call_handler_async(func, owner, *pargs, **kwargs)
            else:
                _call_handler_sync(func, owner, *pargs, **kwargs)

    def __call__(self, *pargs, **kwargs):
        """
        Syntactic sugar for :meth:`trigger`
        """
        self.trigger(*pargs, **kwargs)

    def handler(self, callable, *, weak: bool = False):
        """
        Registers a handler.

        If ``weak`` is True, keep a weakref to the handler instead of a
        strong one.

        Args:
            callable: Function to call when event is emitted.
            weak: Should we keep a strong or weak ref?
        """
        if weak:
            if isinstance(callable, types.MethodType):
                self.add(weakref.WeakMethod(callable, lambda ref: self.remove(ref)))
            else:
                self.add(weakref.ref(callable, lambda ref: self.remove(ref)))
        else:
            self.add(callable)
        return callable


class Event(BoundEvent):
    """
    An event that an object may fire.

    Acts as a set for registered events.

    Acts as a property descriptor, producing :class:`BoundEvent`
    """
    __name__: str
    __qualname__: str

    def __init__(self, doc: str | None = None):
        super().__init__(doc)
        self._instman = weakref.WeakKeyDictionary()

    def __set_name__(self, owner: type, name: str):
        self.__name__ = name
        self.__qualname__ = f"{owner.__qualname__}.{name}"

    def __get__(self, obj, type=None) -> BoundEvent:
        if obj is None:
            return self
        elif obj not in self._instman:
            self._instman[obj] = BoundEvent(self.__doc__, self, obj)
        return self._instman[obj]

    def __set__(self, obj, value):
        # This is so that this appears as a data descriptor.
        raise AttributeError("Can't set an event")
