"""Inspect locals example."""

from typing import Any

from pysvt import test

d: dict[str, Any] = {
    "i": [[]],
    "o": [5],
}


@test(data=d, show_locals=True)
def hello():
    """Inspect local variables.

    :return: Hardcoded integer
    """
    a = 5

    for _i in range(5):
        a += 1
    print("Hello, World!")

    return 5
