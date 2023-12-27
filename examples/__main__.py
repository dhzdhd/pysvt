import itertools as it
import time

from pysut import test


def key(x):
    t1 = x[0]
    t2 = x[1]

    return abs(t2[0] - t1[0]) * abs(t2[1] - t1[1])


@test("examples/input1.toml", "max_area", True)
class Solution:
    def __init__(self, a: int, b: str) -> None:
        pass

    def max_area(self, height: list[int], amount: int) -> int:
        # time.sleep(1)
        choices = list(it.combinations(enumerate(height), amount))
        m = max(choices, key=key)

        t1 = m[0]
        t2 = m[1]
        return abs(t2[0] - t1[0]) * abs(t2[1] - t1[1]) + 1


# @test("examples/input2.toml")
def max_area(height: list[int], amount: int) -> int:
    time.sleep(1)
    choices = list(it.combinations(enumerate(height), amount))
    m = max(choices, key=key)

    t1 = m[0]
    t2 = m[1]
    return abs(t2[0] - t1[0]) * abs(t2[1] - t1[1]) + 1
