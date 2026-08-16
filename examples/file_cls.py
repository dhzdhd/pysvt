"""Class-based test case example using file data.

This example demonstrates how to load test cases from a TOML file
for a class method using the `method` parameter.
"""

from pysvt import test


# Use this instead if you want to use a different TOML format
# @test("data/data_cases.toml")
@test(file="examples/data/data.toml", method="func")
class Demo:
    """Demo class containing a method to test."""

    def func(self, arg1: int, arg2: int) -> int:
        """Add two integers together.

        :param arg1: The first integer operand.
        :param arg2: The second integer operand.
        :return: The sum of arg1 and arg2.
        """
        return arg1 + arg2
