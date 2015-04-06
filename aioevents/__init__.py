"""
Events for asyncio

In order for your class to have an event, just use it like so:

class Spam:
    egged = Event("The spam has been egged")

To trigger an event, just call it like a method:
>>> Spam().egged(5)

All the positional and keyword arguments get passed to the handlers.

To register an event handler, use the .handler() decorator method:

   myspam = Spam()

   @myspam.egged.handler
   def gotegged(amount):
       print("I got egged: {}".format(amount))

It also works on the class level:
* Handlers registered on the class get called for every instance and
  (TODO) receives the instance as the first argument or None
* Triggering on a class only calls class-level handlers
"""

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
import asyncio
import weakref
__all__ = 'Event',


class BoundEvent(set):
    """
    A bound event. Also acts as the base for unbound events.

    Acts as a set for registered handlers.
    """
    def __init__(self, doc, parent=None):
        self.__doc__ = "Event: " + doc
        self._pman = parent

    def trigger(self, *pargs, **kwargs):
        """e.trigger(...) -> None
        Schedules the calling of all the registered handlers. Exceptions are
        consumed.

        Uses BaseEventLoop.call_soon().
        """
        if self._pman is not None:
            self._pman.trigger(*pargs, **kwargs)
        el = asyncio.get_event_loop()
        for handler in self:
            el.call_soon_threadsafe(handler, *pargs, **kwargs)

    def __call__(self, *pargs, **kwargs):
        """
        Syntactic sugar for trigger()
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
        Similar to trigger(), but yields the results of each handler in turn.

        Unlike trigger(), the event loop is not used. If the iteration is
        cancelled early, no further handlers are called. If a handler throws an
        exception, it propogates to the caller.

        any() and all() do work as expected.
        """
        if self._pman is not None:
            yield from self._pman.calleach(*pargs, **kwargs)
        for handler in self:
            yield handler(*pargs, **kwargs)


class Event(BoundEvent):
    def __init__(self, doc):
        super().__init__(doc)
        self._instman = weakref.WeakKeyDictionary()

    def __get__(self, obj, type=None):
        if obj is None:
            return self
        elif obj not in self._instman:
            self._instman[obj] = BoundEvent(self.__doc__, self)
        return self._instman[obj]

    def __set__(self, obj, value):
        # This is so that this appears as a data descriptor.
        raise AttributeError("Can't set an event")
