"""Stdout capture example.

This example demonstrates how pysvt captures stdout output during
test execution and displays it in the test results.
"""

from pysvt import test

data = {
    "name": ["Normal case", "Edge case"],
    "i": [[1, 2], [2, 3]],
    "o": [2, 5],
    "metadata": ["Basic addition functionality", "Basic addition functionality"],
}


@test(data=data)
def func(arg1: int, arg2: int) -> int:
    """Add two integers and print the arguments to stdout.

    :param arg1: The first integer operand.
    :param arg2: The second integer operand.
    :return: The sum of arg1 and arg2.
    """
    print(f"Arg 1: {arg1}")
    print(f"Arg 2: {arg2}")
    return arg1 + arg2
