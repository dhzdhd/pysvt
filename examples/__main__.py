from pysut import Test
import itertools as it


def key(x):
    t1 = x[0]
    t2 = x[1]

    return abs(t2[0] - t1[0]) * abs(t2[1] - t1[1])


class Solution:
    @Test("examples/input1.toml")
    @Test("examples/input2.toml")
    @Test("examples/input3.toml")
    def maxArea(self, height: [int], amount: int) -> int:
        choices = list(it.combinations(enumerate(height), amount))
        m = max(choices, key=key)

        t1 = m[0]
        t2 = m[1]
        return abs(t2[0] - t1[0]) * abs(t2[1] - t1[1]) + 1

    # @Test("examples/input.toml")
    # def a(self) -> int:
    #     return 1


sol = Solution()
print(sol.maxArea([1, 8, 6, 2, 5, 4, 8, 3, 7], 2))
print(sol.maxArea([1, 2, 1], 2))
# print(sol.a())
