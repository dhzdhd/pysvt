"""Error example."""

from pysvt import test

data = {
    "name": ["Normal case", "Edge case"],
    "i": [[1, 2], [2, 3]],
    "o": [2, 5],
    "metadata": ["Basic addition functionality", "Basic addition functionality"],
}


@test(data=data)
def func(arg1: int, arg2: int) -> int:
    """Deliberately raise a `TypeError` to test error-handling behavior.

    :param arg1: The first integer operand.
    :param arg2: The second integer operand.
    :return: Never returns; always raises `TypeError`.
    :raises TypeError: Always, to simulate a failing test case.
    """
    raise TypeError("this is an error")
    return arg1 + arg2
