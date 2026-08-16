"""Preprocess and postprocess example.

This example demonstrates how to use preprocess and postprocess functions
to transform test input data before the test runs and transform the output
after the test runs, useful for testing functions that work with different
data representations.
"""

from pysvt import test


def preprocess(string: str) -> list[str]:
    """Convert a string into a list of characters.

    :param string: Input string to split.
    :return: List of individual characters.
    """
    return list(string)


def postprocess(lst: list[str]) -> str:
    """Join a list of characters back into a string.

    :param lst: List of characters to join.
    :return: Concatenated string.
    """
    return "".join(lst)


@test(
    file="examples/data/prepostprocess.toml",
    preprocess=preprocess,
    postprocess=postprocess,
)
def func(arg1: list[str], arg2: list[str]) -> list[str]:
    """Concatenate two lists of characters.

    :param arg1: First list of characters.
    :param arg2: Second list of characters.
    :return: Concatenated list.
    """
    new = arg1 + arg2
    return new
