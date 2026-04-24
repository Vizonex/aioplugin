"""
aioplugin
---------

An asynchronous application builder tool for different asynchronous programs.
It is compatable with trio, anyio & also asyncio.
"""

from .event import event
from .plugin import Plugin

__author__ = "Vizonex"
__version__ = "0.3.2"
__all__ = ("event", "Plugin")
