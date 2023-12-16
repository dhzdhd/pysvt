import itertools as it
import time

from pysut import test_fn, test_cls


def key(x):
    t1 = x[0]
    t2 = x[1]

    return abs(t2[0] - t1[0]) * abs(t2[1] - t1[1])


@test_cls("examples/input2.toml", "max_area")
class Solution:
    def __init__(self, a: int, b: str) -> None:
        pass

    def max_area(self, height: [int], amount: int) -> int:
        time.sleep(1)
        choices = list(it.combinations(enumerate(height), amount))
        m = max(choices, key=key)

        t1 = m[0]
        t2 = m[1]
        return abs(t2[0] - t1[0]) * abs(t2[1] - t1[1]) + 1


# @test_fn("examples/input2.toml")
def max_area(height: [int], amount: int) -> int:
    time.sleep(1)
    choices = list(it.combinations(enumerate(height), amount))
    m = max(choices, key=key)

    t1 = m[0]
    t2 = m[1]
    return abs(t2[0] - t1[0]) * abs(t2[1] - t1[1]) + 1
