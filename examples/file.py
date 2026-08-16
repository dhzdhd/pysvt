"""File-based test case example.

This example demonstrates how to load test cases from a TOML file
instead of defining them inline in a dictionary.
"""

from pysvt import test


# Use this instead if you want to use a different TOML format
# @test("data/data_cases.toml")
@test(file="examples/data/data.toml")
def func(arg1: int, arg2: int) -> int:
    """Add two integers together.

    :param arg1: The first integer operand.
    :param arg2: The second integer operand.
    :return: The sum of arg1 and arg2.
    """
    return arg1 + arg2
