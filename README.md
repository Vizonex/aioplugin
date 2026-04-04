# AioPlugin

A tool inspired by the way pluggy works with pytest but is meant to help build application-like 
builds using asynchronous event wrappers. It is the successor to aiocallback as it's primary rewrite. 
Libraries such as freezabledict2, frozenlist and reductable-params act as a few of the library's 
primary resources and backbones.

It takes inspiration from the popular discord.py and pluggy libraries allowing you to build very
cleaver asynchronous programs. It can be ran in some very unique ways and allows for other 
developers to add on to your library's callbacks in some very clean and surprising ways.


It can be used with virtually any asynchronous implementations as long as it uses the `await` 
syntax. A few examples would include, anyio, trio and asyncio, curio and twisted are not tested but I can 
gaurentee that it is likely to work with those implementations too.


## Small example

```python
from aioplugin.event import event
from aioplugin.plugin import Plugin


class MyEvent(Plugin):
    # you can very easily add your own data, it's recommended 
    # to use typing.Generic for the best results if the data 
    # can be combined to other events.
    def __init__(self, items):
        super().__init__()
        self._items = items

    @event
    async def on_name(self, name: str) -> None:
        pass


events = MyEvent()

print(events.__event_names__)


@events.on_name
async def hello(name: str):
    print(f"Hello {name}")


async def main():
    # Like aiosignal this comes with it's own freezing funciton. 
    # This is inspired by aiocallback as aioplugin was meant 
    # to remedy some of aiocallback's shortcomings and other various bugs.
    events.freeze()
    await events.on_name.send("World!")


if __name__ == "__main__":
    import winloop

    winloop.run(main())
```

There is much more documentation is coming soon.
