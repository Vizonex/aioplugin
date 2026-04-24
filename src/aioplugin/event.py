from __future__ import annotations

import sys
from collections.abc import Awaitable, Callable, MutableMapping
from typing import Any, Concatenate, Generic, Protocol, overload

from .paramsignal import _P, ParamSignal

if sys.version_info >= (3, 11):
    from typing import Self
else:
    Self = Any


class _EventImpl(Protocol):
    _events: MutableMapping[str, ParamSignal[...]]


class event(Generic[_P]):
    """shares simillar tooling to propcache but
    it is used for wrapping and storing events"""

    def __init__(
        self, wrapped: Callable[Concatenate[Any, _P], Awaitable[object]]
    ) -> None:
        self.__wrapped__ = wrapped
        self.__doc__ = wrapped.__doc__
        self.name = wrapped.__name__

    @overload
    def __get__(
        self, inst: None, owner: type[object] | None = None
    ) -> Self: ...

    @overload
    def __get__(
        self, inst: _EventImpl, owner: type[object] | None = None
    ) -> ParamSignal[_P]: ...

    def __get__(
        self, inst: _EventImpl | None, owner: type[object] | None = None
    ) -> ParamSignal[_P] | Self:
        if inst is None:
            return self
        try:
            return inst._events[self.name]  # type: ignore[no-any-return]
        except KeyError:
            return inst._events.setdefault(
                self.name, ParamSignal(inst, self.__wrapped__)
            )

    def __set__(self, inst: _EventImpl, value: ParamSignal[_P]) -> None:
        raise AttributeError("event property is read-only.")
