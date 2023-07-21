"""
Events for asyncio

In order for your class to have an event, just use it like so::

    class Spam:
        egged = Event("The spam has been egged")

To trigger an event, just call it like a method::

    >>> Spam().egged(5)

All the positional and keyword arguments get passed to the handlers.

To register an event handler, use the .handler() decorator method::

   myspam = Spam()

   @myspam.egged.handler
   def gotegged(amount):
       print("I got egged: {}".format(amount))

It also works on the class level:

* Handlers registered on the class get called for every instance and (TODO)
  receives the instance as the first argument or None
* Triggering on a class only calls class-level handlers
"""

import asyncio
import functools
import logging
import weakref
__all__ = 'Event',

LOG = logging.getLogger(__name__)

"""
About References

Just to document how references are managed:

The class strongly references the unbound Event
The Event holds a dictionary of weakly referenced keys to Instances mapping to
strong references of bound events.
Bound events hold strong references registered callables.

A strong reference of a handler does not need to be kept by the application.

When an instance is freed, its keys in the bound events tables are freed, and
the bound events are collected. Registered handlers are unrefed and possibly
freed.

When a class is freed (all instances already collected), the unbound events are
collected. Again, handlers are left to fend for themselves.
"""


class BoundEvent(set):
    """
    A bound event, produced when :class:`Event` is used as a property on an instance.

    Acts as a set for registered handlers.
    """
    __doc__: str

    def __init__(self, doc: str | None = None, parent: 'Event | None' = None):
        if isinstance(doc, str):
            if not doc.startswith("Event:"):
                doc = f"Event: {doc}"  # I'm not completely convinced this is a good idea
            self.__doc__ = doc
        self._pman = parent
        if parent is not None:
            self.__name__ = parent.__name__
            self.__qualname__ = parent.__qualname__

    def trigger(self, *pargs, **kwargs) -> None:
        """
        Schedules the calling of all the registered handlers. Exceptions are
        consumed.

        Uses :meth:`~asyncio.loop.call_soon_threadsafe` if the event loop is running,
        otherwise calls handlers directly.
        """
        if self._pman is not None:
            self._pman.trigger(*pargs, **kwargs)
        el = asyncio.get_event_loop()
        if el is not None and el.is_running():
            for handler in self:
                el.call_soon_threadsafe(functools.partial(handler, *pargs, **kwargs))
        else:
            for handler in self:
                try:
                    handler(*pargs, **kwargs)
                except Exception:
                    LOG.exception("Swallowed exception in event handler")

    def __call__(self, *pargs, **kwargs):
        """
        Syntactic sugar for :meth:`trigger`
        """
        self.trigger(*pargs, **kwargs)

    def handler(self, callable):
        """
        Registers a handler
        """
        self.add(callable)
        return callable

    def calleach(self, *pargs, **kwargs):
        """
        Similar to :meth:`trigger`, but yields the results of each handler in turn.

        Unlike :meth:`trigger`, the event loop is not used. If the iteration is
        cancelled early, no further handlers are called. If a handler throws an
        exception, it propogates to the caller.

        :func:`any` and :func:`all` do work as expected.
        """
        if self._pman is not None:
            yield from self._pman.calleach(*pargs, **kwargs)
        for handler in self:
            yield handler(*pargs, **kwargs)


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
            self._instman[obj] = BoundEvent(self.__doc__, self)
        return self._instman[obj]

    def __set__(self, obj, value):
        # This is so that this appears as a data descriptor.
        raise AttributeError("Can't set an event")
