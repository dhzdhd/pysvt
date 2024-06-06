from pysvt import test

data = {
    "name": ["Normal case", "Edge case"],
    "i": [[1, 2], [2, 3]],
    "o": [2, 5],
    "metadata": ["Basic addition functionality", "Basic addition functionality"],
}


@test(data=data)
def func(arg1: int, arg2: int) -> int:
    print(f"Arg 1: {arg1}")
    print(f"Arg 2: {arg2}")
    return arg1 + arg2
