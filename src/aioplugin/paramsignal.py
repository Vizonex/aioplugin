"""
Paramspec version of aiosignal, it uses a special system for allowing parameter
customization while allowing the end developer to access important typehints.
"""

from __future__ import annotations

from collections.abc import Awaitable, Callable, Coroutine
from contextlib import AbstractAsyncContextManager, asynccontextmanager
from typing import Any, Generic, ParamSpec, TypeVar, cast

from aiocallback.hooks import Hook, is_asynccontextmanagerfunction
from frozenlist import FrozenList
from reductable_params import reduce

# overloaders so that different parameter names or formations can be used,
# also for usage with hooks
_P = ParamSpec("_P")
_P2 = ParamSpec("_P2")
_T = TypeVar("_T")


# Having paramspec benefits the programmer developing the application
# and the developer using the application. Having a 2 way system that provides
# the right typehints can be the hardest part. We have a system that enables
# user-devs to rearrange and filter parameters however they please and add
# additional items using a hooking system to behave simillar to pytest's
# fixtures allowing for any additional items to be taken if needed.


class ParamSignal(Generic[_P], FrozenList[Callable[..., Awaitable[object]]]):
    """A Coroutine-based signal implementation that relys on a parent
    to help define what parameters should be passed enabling typehints for
    positional and keyword arguments."""

    __slots__ = ("_parent", "_hooks", "_owner")

    def __init__(
        self, owner: object, func: Callable[_P, Awaitable[object]]
    ) -> None:
        super().__init__()
        self._owner = owner
        self._parent = reduce(func)
        self._hooks: Hook[dict[str, Any]] = Hook(owner)

    def __call__(
        self, func: Callable[_P2, Coroutine[Any, Any, _T]]
    ) -> Callable[_P2, Coroutine[Any, Any, _T]]:
        """Decorator for adding a callback for this signal. It will be wrapped
        in a reduce class to only obtain needed parameters"""
        # Just lie to it. Hooks can enable take dynamic arguments anyways...
        self.append(cast(Callable[_P, Coroutine[Any, Any, object]], func))
        return func

    def hook(
        self, func: Callable[_P2, AbstractAsyncContextManager[_T]]
    ) -> Callable[_P2, AbstractAsyncContextManager[_T]]:
        """
        Registers a new context manager to use it will use the
        function's name to be the registered key, it can also return
        back the function that was sent allowing it to be optionally
        used elsewhere.
        """
        wrapped = (
            asynccontextmanager(func)
            if not is_asynccontextmanagerfunction(func)
            else func
        )
        self._hooks[func.__name__] = reduce(wrapped)
        return func

    def freeze(self) -> None:
        """freezes callbacks"""
        # replace functions with reduce after editing them so
        # that custom data can be safely taken in it's place.
        items = list(map(reduce, self))
        self.clear()
        self.extend(items)
        self._hooks.freeze()
        super().freeze()

    async def send(self, *args: _P.args, **kwargs: _P.kwargs) -> None:
        if not self.frozen:
            raise RuntimeError("Cannot send a non-frozen signal.")
        if not (self or self._hooks):
            # Empty, do not continue
            return
        params = self._parent.install(*args, **kwargs)

        # Install any other hooks that are seen
        # before the final sendoff takes place...
        async with self._hooks.send(params) as hooks:
            params.update(hooks)

            for s in self:
                # these are actually FrozenList[reduce] so calling it shouldn't
                # require unpacking. I just didn't feel like typehinting it...
                await s(params)

    def __repr__(self) -> str:
        return "<{} owner={}, frozen={}, hooks={!r}, {!r}>".format(
            self.__class__.__name__,
            self._owner,
            self.frozen,
            self._hooks,
            list(self)
            if not self.frozen
            else [getattr(s, "__wrapper__", s) for s in self],
        )
