# AioPlugin

[![PyPI version](https://badge.fury.io/py/aioplugin.svg)](https://badge.fury.io/py/aioplugin)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/aioplugin)](https://pypi.org/project/aioplugin)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![IDIM](https://raw.githubusercontent.com/Vizonex/IDIM-Badge/master/badge.svg)](https://github.com/Vizonex/IDIM-Badge)


A tool inspired by the way pluggy works with pytest but is meant to help build application-like 
builds using asynchronous event wrappers. It is the successor to [aiocallback](https://github.com/Vizonex/aiocallback) as it's primary rewrite, however aiocallback does plan to get some of this project's backend stuff in the future so that aiocallback never goes stale but helps keep aioplugin a bit more neat and organized.


It takes inspiration from the popular discord.py and pluggy libraries allowing you to build very
cleaver asynchronous programs. It can be ran in some very unique ways and allows for other 
developers to add on to your application's callbacks in some very clean/unique and surprising ways.


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

## Other Dependencies

Libraries such as these are the library's main back bones. They were developed for this library specifically with very a tiny footprint, these will not eat diskspace at all if this was your primary concern, these were seperated specifically if developers had something else in mind:

- [freezabledict2](https://github.com/Vizonex/freezabledict2) there were so many names taken so many times that a #2 was needed. It works the same way as FrozenList giving the option to mutate a dictionary/hash-table until frozen.

- [reductable-params](https://github.com/Vizonex/reductable-params) This library is the main tool responsible for giving developers like you the freedom of positioning parameters however you want or ignore them or create custom parameters using hooks. If you want to make your own stuff, reductable-params is perfect for writing your own callable plugin systems and has powerful performance benefits thanks to it's use of C & Cython, it also has a pure python fallback if you plan to use something a little bit more unsupported like pypy. 

