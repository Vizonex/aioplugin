import pytest

from aioplugin.paramsignal import ParamSignal

# test is modeled after aiosignal to save some headaches with testing...

pytestmark = pytest.mark.anyio


class Owner:
    def __repr__(self) -> str:
        return "<Owner 0xdeadbeef>"


@pytest.fixture
def owner() -> Owner:
    return Owner()


async def test_signal_positional_args(owner: Owner) -> None:
    async def callback(a: int, b: str) -> None:
        return

    # ParamSignal[(a: int, b: str)]
    signal = ParamSignal(owner, callback)
    signal.append(callback)
    signal.freeze()
    await signal.send(42, "foo")


async def test_add_signal_handler_not_a_callable(owner: Owner) -> None:
    async def foo() -> None:
        pass

    callback = True
    signal = ParamSignal(owner, foo)
    signal.append(callback)  # type: ignore[arg-type]
    signal.freeze()
    with pytest.raises(TypeError):
        await signal.send()


async def test_function_signal_dispatch_kwargs(owner: Owner) -> None:
    async def signature(foo: int, bar: int) -> None:
        pass

    signal = ParamSignal(owner, signature)
    kwargs = {"foo": 1, "bar": 2}

    async def callback(foo: int, bar: int) -> None:
        assert foo == 1
        assert bar == 2

    signal.append(callback)
    signal.freeze()

    await signal.send(**kwargs)


# TODO: This is broken because we changed up the backend very good...
# def test_repr(owner: Owner) -> None:
#     async def foo(args) -> None:
#         pass

#     signal = ParamSignal(owner, foo)

#     signal.append(mock.Mock(__repr__=lambda *a: "<callback>"))

#     assert r"<callback>" in repr(signal)


# def test_repr_frozen(owner: Owner) -> None:
#     async def foo(args) -> None:
#         pass

#     signal = ParamSignal(owner, foo)

#     signal.append(mock.Mock(__repr__=lambda *a: "<callback>"))
#     signal.freeze()
#     assert r"<reduc" in repr(signal)


async def test_decorator_callback_dispatch_args_kwargs(owner: Owner) -> None:

    async def sig(a: int, b: int, c: str = "", d: str = "world") -> None:
        assert a == 1
        assert b == 2
        assert c == "Hello"
        assert d == "world"

    signal = ParamSignal(owner, sig)
    signal.append(sig)
    signal.freeze()
    await signal.send(1, 2, "Hello")
    await signal.send(a=1, b=2, c="Hello")
    await signal.send(1, 2, "Hello", "world")
