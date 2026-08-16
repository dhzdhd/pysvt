"""Class-based test case example using dictionary data.

This example demonstrates how to define test cases for a class method
using a dictionary with the `method` parameter.
"""

from pysvt import test

data = {
    "name": ["Normal case", "Edge case"],
    "i": [[1, 2], [2, 3]],
    "o": [2, 3],
    "metadata": ["Basic addition functionality", "Basic addition functionality"],
}


@test(data=data, method="func")
class Demo:
    """Demo class containing a method to test."""

    def func(self, arg1: int, arg2: int) -> int:
        """Add two integers together.

        :param arg1: The first integer operand.
        :param arg2: The second integer operand.
        :return: The sum of arg1 and arg2.
        """
        return arg1 + arg2
