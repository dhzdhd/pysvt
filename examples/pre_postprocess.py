from pysvt import test


def preprocess(string: str) -> list[str]:
    return list(string)


def postprocess(lst: list[str]) -> str:
    return "".join(lst)


@test(
    file="examples/data/prepostprocess.toml",
    preprocess=preprocess,
    postprocess=postprocess,
)
def func(arg1: list[str], arg2: list[str]) -> list[str]:
    new = arg1 + arg2
    return new
