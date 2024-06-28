from pysvt import test


# Use this instead if you want to use a different TOML format
# @test("data/data_cases.toml", is_live=True)
@test("data/data.toml", is_live=True)
def func(arg1: int, arg2: int) -> int:
    return arg1 + arg2
