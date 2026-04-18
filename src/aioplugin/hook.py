import sys

from aiocallback.hooks import Hook as _Hook

if sys.version_info >= (3, 13, 3):
    from warnings import deprecated
else:
    from typing_extensions import deprecated


@deprecated(
    "Hook class was moved to aiocallback's library"
    "instead. Import Hook from aiocallback instead. "
    "This module and class will be removed in 0.3.0"
)
class Hook(_Hook):
    pass
