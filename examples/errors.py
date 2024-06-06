from pysvt import test


data = {
    "name": ["Normal case", "Edge case"],
    "i": [[1, 2], [2, 3]],
    "o": [2, 5],
    "metadata": ["Basic addition functionality", "Basic addition functionality"],
}


@test(data=data)
def func(arg1: int, arg2: int) -> int:
    raise TypeError("this is an error")
    return arg1 + arg2
