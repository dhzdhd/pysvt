"""Recursive function test example.

This example demonstrates testing a recursive function that reverses
a list using an accumulator pattern.
"""

from pysvt import test

d = {
    "i": [[[1, 2, 3]], [[1, 4, 3, 2]]],
    "o": [[3, 2, 1], [2, 3, 4, 1]],
}


def reverse(xs: list[int], acc: list[int]) -> list[int]:
    """Recursively reverse a list by popping elements onto an accumulator.

    :param xs: The list of integers to reverse.
    :param acc: The accumulator holding reversed elements so far.
    :return: The fully reversed list once `xs` is empty.
    """
    if xs == []:
        return acc
    print(f"xs: {xs}, acc: {acc}")
    el = xs.pop()
    return reverse(xs, [*acc, el])


@test(data=d)
def reverseArray(a: list[int]) -> list[int]:
    """Reverse the input array using the `reverse` helper.

    :param a: The list of integers to reverse.
    :return: The reversed list.
    """
    return reverse(a, [])
