import itertools as it
import time

from pysvt import test

data = {
    "cases": [
        {
            "name": "test case 1",
            "init": [1, 2],
            "inputs": [[1, 8, 6, 2, 5, 4, 8, 3, 7], 2],
            "outputs": 49,
            "metadata": "Basic addition functionality",
        },
        {
            "name": "test case 2",
            "init": [1, 2],
            "i": [[1, 2, 1], 2],
            "o": 5,
            "metadata": "Division with zero",
        },
        {
            "name": "test case 3",
            "init": [1, 7],
            "input": [[1, 2, 3, 1], 2],
            "output": 3,
            "metadata": "Custom comparison logic",
        },
    ]
}


def key(x):
    t1 = x[0]
    t2 = x[1]

    return abs(t2[0] - t1[0]) * abs(t2[1] - t1[1])


@test(data=data, method="max_area", error_only=True)
# @test(file="examples/input1.toml", method="max_area", error_only=True)
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
