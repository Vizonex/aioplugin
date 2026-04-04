from typing import Any

from attrs import define, field
from freezabledict import FrozenDict

from .paramsignal import ParamSignal
from .plugin import AbstractPlugin


@define
class AttrsPlugin(AbstractPlugin):
    """Use if your main plugin object requires the use of attrs object."""

    _events: FrozenDict[str, ParamSignal[...]] = field(
        factory=FrozenDict, init=False
    )
    _plugins: FrozenDict[str, object] = field(factory=FrozenDict, init=False)
    _cache: dict[str, Any] = field(factory=dict, init=False)


@define(slots=True)
class AttrsSlotsPlugin(AbstractPlugin):
    """Use if your main plugin object requires the use of attrs object with slots enabled."""

    _events: FrozenDict[str, ParamSignal[...]] = field(
        factory=FrozenDict, init=False
    )
    _plugins: FrozenDict[str, object] = field(factory=FrozenDict, init=False)
    _cache: dict[str, Any] = field(factory=dict, init=False)
