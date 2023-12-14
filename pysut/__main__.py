from typing import Callable, Any
import tomllib as toml
from pathlib import Path
from functools import wraps
from pysut.utils import load_toml

type Function = Callable[..., Any]


class Test:
    called = []

    def __init__(self, file: str | Path) -> None:
        assert isinstance(file, Path) or isinstance(file, str)

        if not isinstance(file, Path):
            self._file = Path(file)
        else:
            self._file = file
        self._inputs: list[str] | None = None
        self._outputs: list[str] = []

    def __call__(self, func: Function) -> Any:
        @wraps(func)
        def wrapper(*args, **kwargs):
            if id(func) in Test.called:
                return func(*args, **kwargs)

            Test.called.append(id(func))
            print(load_toml(self._file))

            return func(*args, **kwargs)

        return wrapper


def test(file: str | Path):
    print(load_toml(file))

    def deco(func: Function):
        return func

    return deco
