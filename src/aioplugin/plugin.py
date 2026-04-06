from __future__ import annotations

import inspect
from abc import ABC
from typing import cast

from freezabledict import FrozenDict
from propcache import under_cached_property

from .event import event
from .paramsignal import ParamSignal


# incase needed ABC is also added for allowing developers to easily add in
# abstract methods.
class AbstractPlugin(ABC):
    """a Useful class for creating applications with arbitarary
    callbacks for wrapping to event objects"""

    def __plugin_init__(self) -> None:
        """
        Seperate function to inialize plugin related objects,
        incase somehting like a dataclass or attrs-like object
        needs to be used. you can hook this to `__post_init__`
        or `__attrs_post_init__` as needed.
        """

        self._events: FrozenDict[str, ParamSignal[...]] = FrozenDict()
        # plugins set to be used with this object.
        self._plugins: FrozenDict[str, object] = FrozenDict()
        self._cache = {}

    @under_cached_property
    def __event_names__(self) -> frozenset[str]:
        """lists out all event attributes related to this specific object"""
        cls = self.__class__
        # the goal is not to end up trip-wiring anything so check for attributes
        # at the type-level.
        return frozenset(
            {
                attr
                for attr in dir(self)
                if isinstance(getattr(cls, attr, None), event)
            }
        )

    @property
    def frozen(self) -> bool:
        """Checks to see if all events have been frozen or not"""
        return (
            all(
                [cast(ParamSignal[...], e).frozen for e in self.__event_names__]
            )
            and self._events.frozen
            and self._plugins.frozen
        )

    def freeze(self):
        """Freezes all events wrapped to this specific object"""
        for e in self.__event_names__:
            cast(ParamSignal[...], getattr(self, e)).freeze()

        # do not allow the events be tampered with after being frozen over
        self._events.freeze()
        self._plugins.freeze()

    # TODO: Documentation on why plugins do not wrap classes and why type-level
    # mixing is bad!
    def add_plugin(self, obj: object, name: str | None = None) -> None:
        """Adds an object's functions to a given"""
        if self._plugins.frozen:
            raise RuntimeError("Cannot modify frozen plugins.")

        name = name if name else obj.__class__.__name__

        if name in self._plugins:
            raise RuntimeError(f"plugin {name!r} already registered.")

        for e in self.__event_names__:
            if func := getattr(obj, e, None):
                if inspect.isroutine(func):
                    # Register class's asynchronous function.
                    # TODO: add an asynchronous check?
                    cast(ParamSignal[...], getattr(self, e)).__call__(func)

        # keep a reference to this object so that it doesn't go missing.
        self._plugins[name] = obj

    def remove_plugin(self, name: str | None = None) -> None:
        """remove an object's functions to this plugin"""
        if self._plugins.frozen:
            raise RuntimeError("Cannot modify frozen plugins.")

        if name not in self._plugins:
            raise RuntimeError(f"plugin {name!r} not registered.")

        obj = self._plugins.pop(name)

        for e in self.__event_names__:
            if func := getattr(obj, e, None):
                if inspect.isroutine(func):
                    cast(ParamSignal[...], getattr(self, e)).remove(func)


class Plugin(AbstractPlugin):
    __slots__ = ("_events", "_plugins", "_cache")

    def __init__(self) -> None:
        self.__plugin_init__()
