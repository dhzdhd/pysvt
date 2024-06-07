from pysvt import test

d = {
    "i": [[[1, 2, 3]], [[1, 4, 3, 2]]],
    "o": [[3, 2, 1], [2, 3, 4, 1]],
}


def reverse(xs: list, acc: list = []) -> list:
    if xs == []:
        return acc
    print(f"xs: {xs}, acc: {acc}")
    el = xs.pop()
    return reverse(xs, [*acc, el])


@test(data=d)
def reverseArray(a: list):
    return reverse(a)
