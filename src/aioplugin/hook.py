from __future__ import annotations

import inspect
import sys
from collections.abc import AsyncIterator, Callable
from contextlib import (
    AbstractAsyncContextManager,
    AsyncExitStack,
    asynccontextmanager,
)

from freezabledict import FrozenDict

if sys.version_info >= (3, 11):
    from typing import Unpack  # pragma: no cover - version differences
else:
    from typing_extensions import Unpack

if sys.version_info >= (3, 13):
    from typing import TypeVarTuple  # pragma: no cover - version differences
else:
    from typing_extensions import TypeVarTuple

_Ts = TypeVarTuple("_Ts", default=Unpack[tuple[()]])


def is_asynccontextmanagerfunction(obj: object) -> bool:
    """Attempts to  see if object is possibly with an asynccontextmanager wrapper or not"""
    return (
        inspect.isasyncgenfunction(obj.__wrapped__)
        if hasattr(obj, "__wrapped__")
        else False
    )


class Hook(
    FrozenDict[
        str, Callable[[Unpack[_Ts]], AbstractAsyncContextManager[object]]
    ]
):
    """Hook for calling back multiple context manager-like fixtures"""

    def __init__(self, owner: object) -> None:
        super().__init__()
        self._owner = owner

    def __repr__(self):
        return "<{}(frozen={}, owner={}, {!r})".format(
            self.__class__.__name__, self._frozen, self._owner, self._items
        )

    @asynccontextmanager
    async def send(
        self, *args: Unpack[_Ts], **kwargs
    ) -> AsyncIterator[dict[str, object]]:
        """Sends all life-cycles and returns them for use elsewhere as a dictionary object"""
        if not self.frozen:
            raise RuntimeError("Cannot enter into non-frozen life-cycle.")

        async with AsyncExitStack() as s:
            yield {
                name: await s.enter_async_context(cm(*args, **kwargs))
                for name, cm in self.items()
            }
