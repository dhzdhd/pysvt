from pysvt import test

d = {
    "i": [[]],
    "o": [5],
}


@test(data=d, show_locals=True)
def hello():
    a = 5

    for _ in range(5):
        a += 1
    print("Hello, World!")

    return 5
