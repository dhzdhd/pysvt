"""Dictionary-based test case example.

This example demonstrates how to define test cases using a dictionary
with keys for inputs, outputs, names, and metadata.
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
    """Add two integers together.

    :param arg1: The first integer operand.
    :param arg2: The second integer operand.
    :return: The sum of arg1 and arg2.
    """
    return arg1 + arg2
