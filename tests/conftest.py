import sys
from importlib.util import find_spec
from typing import Any

import pytest


def has_module(library: str):
    "Finds out if library exists without executing any code for the library."
    return find_spec(library) is not None


PARAMS = [pytest.param(("asyncio", {"use_uvloop": False}), id="asyncio")]

# NOTE: Extensions are optional now...
if has_module("winloop" if sys.platform == "win32" else "uvloop"):
    PARAMS.append(
        pytest.param(("asyncio", {"use_uvloop": True}), id="asyncio+uvloop")
    )

if has_module("trio"):
    PARAMS.append(
        pytest.param(
            ("trio", {"restrict_keyboard_interrupt_to_checkpoints": True}),
            id="trio",
        )
    )


@pytest.fixture(params=PARAMS)
def anyio_backend(request: pytest.FixtureRequest) -> Any:
    return request.param
