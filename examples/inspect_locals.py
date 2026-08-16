"""Inspect locals example.

This example demonstrates how to capture and display local variables
during test execution using the `show_locals=True` parameter.
"""

from typing import Any

from pysvt import test

d: dict[str, Any] = {
    "i": [[]],
    "o": [5],
}


@test(data=d, show_locals=True)
def hello() -> int:
    """Inspect local variables.

    :return: Hardcoded integer 5.
    """
    a = 5

    for _i in range(5):
        a += 1
    print("Hello, World!")

    return 5
