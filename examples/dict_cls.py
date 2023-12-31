from pysvt import test


data = {
    "name": ["Normal case", "Edge case"],
    "i": [[1, 2], [2, 3]],
    "o": [2, 3],
    "metadata": ["Basic addition functionality", "Basic addition functionality"],
}


@test(data=data, method="func")
class Demo:
    def func(self, arg1: int, arg2: int) -> int:
        return arg1 + arg2
