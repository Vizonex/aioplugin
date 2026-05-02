from dataclasses import dataclass, field
from typing import Any

from freezabledict import FrozenDict

from .paramsignal import ParamSignal
from .plugin import AbstractPlugin


@dataclass
class DataclassPlugin(AbstractPlugin):
    """Use if your main plugin object requires the use of dataclasses."""

    _events: FrozenDict[str, ParamSignal[...]] = field(
        default_factory=FrozenDict, init=False
    )
    _plugins: FrozenDict[str, object] = field(
        default_factory=FrozenDict, init=False
    )
    _cache: dict[str, Any] = field(default_factory=dict, init=False)


@dataclass(slots=True)
class DataclassSlotsPlugin(AbstractPlugin):
    """Use if your main plugin object requires the use of dataclasses
    with slots enabled."""

    _events: FrozenDict[str, ParamSignal[...]] = field(
        default_factory=FrozenDict, init=False
    )
    _plugins: FrozenDict[str, object] = field(
        default_factory=FrozenDict, init=False
    )
    _cache: dict[str, Any] = field(default_factory=dict, init=False)
