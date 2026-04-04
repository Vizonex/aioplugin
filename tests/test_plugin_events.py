from aioplugin import Plugin, event
from collections.abc import AsyncIterator
from typing import TypeVar
import pytest

pytestmark = pytest.mark.anyio

T = TypeVar("T")


class Base(Plugin):
    @event
    async def on_event(self, a: str, b: int = 0) -> None: ...

    @event
    async def on_other(self, number: int) -> None: ...


class AdditionalPlugin:
    def __init__(self) -> None:
        self.items = []

    async def on_event(self, a: str, b: int) -> None:
        self.items.append({"a": a, "b": b})

    async def on_other(self, number: int) -> None:
        self.items.append({"number": number})


class AdditionalPlugin2:
    def __init__(self) -> None:
        self.items = []

    async def on_event(self, a: str) -> None:
        self.items.append({"a": a})


@pytest.fixture
def base() -> Base:
    return Base()


@pytest.fixture
def another() -> AdditionalPlugin:
    return AdditionalPlugin()


@pytest.fixture
def another_one() -> AdditionalPlugin2:
    return AdditionalPlugin2()


@pytest.fixture
async def hook_test(base: Base) -> Base:
    @base.on_other.hook
    async def name(number: int) -> AsyncIterator[str]:
        yield str(number)

    @base.on_other
    async def other_event(number: int) -> None:
        assert number == 10

    @base.on_other
    async def other_event_1(name: str) -> None:
        assert name == "10"

    @base.on_other
    async def other_event_2(number: int, name: str) -> None:
        assert number == 10
        assert name == "10"

    return base


async def test_hooks(hook_test: Base) -> None:
    hook_test.freeze()
    await hook_test.on_other.send(10)


async def test_assert_failure(hook_test: Base) -> None:
    hook_test.freeze()
    with pytest.raises(AssertionError):
        await hook_test.on_other.send(0xDEAD)


async def test_events_unfrozen_exception(hook_test: Base) -> None:
    with pytest.raises(RuntimeError, match="Cannot send a non-frozen signal."):
        await hook_test.on_other.send(10)


async def test_defaults(base: Base) -> None:
    # default signatures should not affect what needs to actually be sent.
    # this example attempts to demonstrate this principle with the power
    # of reductable_param's reduce object.

    @base.on_event
    async def on_event(b: int) -> None:
        assert b == 0

    base.freeze()
    await base.on_event.send("You Died!")
    await base.on_event.send(a="You Died!")


def test_disallowing_replacements(base: Base) -> None:
    with pytest.raises(AttributeError, match="event property is read-only."):
        base.on_event = 0xDEAD


class TestAdditionalPlugins:
    def test_adding_plugins(
        self, base: Base, another: AdditionalPlugin
    ) -> None:
        base.add_plugin(another, "another")
        assert "another" in base._plugins

        with pytest.raises(
            RuntimeError, match="plugin 'another' already registered."
        ):
            base.add_plugin(another, "another")

        base.freeze()
        with pytest.raises(
            RuntimeError, match="Cannot modify frozen plugins."
        ):
            base.add_plugin(another, "another")

    def test_removing_plugins(
        self, base: Base, another: AdditionalPlugin
    ) -> None:
        base.add_plugin(another, "another")
        assert "another" in base._plugins
        base.remove_plugin("another")

        with pytest.raises(
            RuntimeError, match="plugin 'another' not registered."
        ):
            base.remove_plugin("another")

        base.freeze()
        with pytest.raises(
            RuntimeError, match="Cannot modify frozen plugins."
        ):
            base.remove_plugin("another")

    async def test_sending_with_plugin(
        self, base: Base, another: AdditionalPlugin
    ) -> None:
        base.add_plugin(another, "another")
        base.freeze()
        await base.on_event.send("1", 2)
        assert another.items == [{"a":"1", "b":2}]

    async def test_sending_with_plugin_2(
        self, base: Base, another: AdditionalPlugin, another_one: AdditionalPlugin2
    ) -> None:
        base.add_plugin(another, "another")
        base.add_plugin(another_one, "another-one")
        base.freeze()
        await base.on_event.send("1", 2)
        await base.on_other.send(number=1)
        # See if events were sent in their correct orders
        assert {"a": "1", "b": 2} in another.items
        assert {"number": 1} in another.items
        assert {"number": 1} not in another_one.items
        assert {"a": "1"} in another_one.items
