from __future__ import annotations
import sys
from collections.abc import Awaitable, Callable, Mapping
from typing import Any, Generic, Protocol, TypeVar, overload

from .paramsignal import _P, ParamSignal

if sys.version_info >= (3, 10):
    from typing import Concatenate
else:
    from typing_extensions import Concatenate

if sys.version_info >= (3, 11):
    from typing import Self
else:
    Self = Any

_Events = TypeVar("_Cache", bound=Mapping[str, ParamSignal[...]])


class _EventImpl(Protocol[_Events]):
    _events: _Events


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
        self, inst: _EventImpl[Any], owner: type[object] | None = None
    ) -> ParamSignal[_P]: ...

    def __get__(
        self, inst: _EventImpl[Any] | None, owner: type[object] | None = None
    ) -> ParamSignal[_P] | Self:
        if inst is None:
            return self
        try:
            return inst._events[self.name]  # type: ignore[no-any-return]
        except KeyError:
            val = ParamSignal(inst, self.__wrapped__)
            inst._events[self.name] = val
            return val

    def __set__(self, inst: _EventImpl, value: ParamSignal[_P]) -> None:
        raise AttributeError("event property is read-only.")
