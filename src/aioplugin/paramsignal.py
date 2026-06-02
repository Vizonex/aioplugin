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
from aiocallback.updater import UpdateSignal
from reductable_params import reduce
from reductable_params.abc import Reducable

# overloaders so that different parameter names or formations can be used,
# also for usage with hooks
_P = ParamSpec("_P")
_P2 = ParamSpec("_P2")
_T = TypeVar("_T")


def _reduce_asynccontextmanager(
    func: Callable[_P2, AbstractAsyncContextManager[_T]],
) -> Reducable[_P2, _T]:
    return reduce(
        asynccontextmanager(func)
        if not is_asynccontextmanagerfunction(func)
        else func
    )


# Having ParamSpec benefits the programmer developing the application
# and the developer using the application. Having a 2 way system that
# provides the right typehints and the right callables can be the
# hardest part.

__all__ = ("ParamSignal", "ParamUpdateSignal")


class ParamSignal(ParentSignal[_P]):
    """A Coroutine-based signal implementation that relys on a parent
    to help define what parameters should be passed enabling typehints for
    positional and keyword arguments."""

    __slots__ = ("_hooks",)

    def __init__(self, owner, parent: Callable[_P, Awaitable[object]]) -> None:
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
        self._hooks[func.__name__] = _reduce_asynccontextmanager(func)
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

        # setup all required parameters needed as well
        # as setting defaults.
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


class ParamUpdateSignal(UpdateSignal[_P]):
    __slots__ = ("_hooks",)

    def __init__(self, owner, parent: Callable[_P, Awaitable[object]]) -> None:
        super().__init__(owner, parent)
        self._hooks: Hook[dict[str, Any]] = Hook(owner)

    async def send_packed(self, data: dict[str, Any]):
        """same as :func:`ParamUpdateSignal.notify`"""
        return await self.notify(data)

    async def send(self, *args: _P.args, **kwargs: _P.kwargs):
        """same as :func:`ParamUpdateSignal.update`"""
        return await self.update(*args, **kwargs)

    async def notify(self, data: dict[str, Any]):
        """
        Notifies updater that a new object is now ready.
        This is mostly an injectable function incase user needs to
        subclass off :class:`ParamUpdateSignal` and provide hooks and
        other tooling for further parameter manipulation.

        :param data: data to send.

        :raises RuntimeError: if signal is not frozen.
        """
        if not self.frozen:
            raise RuntimeError("Cannot send non-frozen signal.")

        async with self._hooks.send(data) as hooks:
            data.update(hooks)
            for s in self.signals:
                await s(data)

    def freeze(self) -> None:
        """freezes callbacks"""
        self._hooks.freeze()
        super().freeze()

    def hook(
        self, func: Callable[_P2, AbstractAsyncContextManager[_T]]
    ) -> Callable[_P2, AbstractAsyncContextManager[_T]]:
        """
        Registers a new context manager to use it will use the
        function's name to be the registered key, it can also return
        back the function that was sent allowing it to be optionally
        used elsewhere.
        """
        self._hooks[func.__name__] = _reduce_asynccontextmanager(func)
        return func

    def __repr__(self) -> str:
        return (
            f"<{self.__class__.__name__} owner={self._owner},"
            f" frozen={self.frozen}, hooks={self._hooks!r}, {list(self)!r}>"
        )
