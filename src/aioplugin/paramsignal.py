"""
Paramspec version of aiosignal, it uses a special system for allowing parameter
customization while allowing the end developer to access important typehints.
"""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from contextlib import AbstractAsyncContextManager, asynccontextmanager
from typing import Any, ParamSpec, TypeVar

from aiocallback.hooks import Hook, is_asynccontextmanagerfunction
from aiocallback.signals import ParentSignal
from reductable_params import reduce

# overloaders so that different parameter names or formations can be used,
# also for usage with hooks
_P = ParamSpec("_P")
_P2 = ParamSpec("_P2")
_T = TypeVar("_T")


# Having ParamSpec benefits the programmer developing the application
# and the developer using the application. Having a 2 way system that
# provides the right typehints and the right callables can be the
# hardest part.


class ParamSignal(ParentSignal[_P]):
    """A Coroutine-based signal implementation that relys on a parent
    to help define what parameters should be passed enabling typehints for
    positional and keyword arguments."""

    __slots__ = ("_hooks",)

    def __init__(self, owner, parent: Callable[_P, Awaitable[object]]):
        super().__init__(owner, parent)
        self._hooks: Hook[dict[str, Any]] = Hook(owner)

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
        self._hooks.freeze()
        super().freeze()

    async def send(self, *args: _P.args, **kwargs: _P.kwargs) -> None:
        if not self.frozen:
            raise RuntimeError("Cannot send a non-frozen signal.")
        if not (self or self._hooks):
            # Empty, do not continue
            return
        params = self.install(*args, **kwargs)

        # Install any other hooks that are seen
        # before the final sendoff takes place...
        async with self._hooks.send(params) as hooks:
            params.update(hooks)

            # Send everything immediately, we already handled all
            # the error checks...
            for s in self.signals:
                await s(params)

    def __repr__(self) -> str:
        return (
            f"<{self.__class__.__name__} owner={self._owner},"
            f" frozen={self.frozen}, hooks={self._hooks!r}, {list(self)!r}>"
        )
