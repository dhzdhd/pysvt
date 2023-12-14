from typing import Callable, Any
import tomllib as toml
from pathlib import Path
from functools import wraps
from pysut.utils import load_toml, parse
from dataclasses import dataclass

type Function = Callable[..., Any]


@dataclass(frozen=True)
class _Model:
    name: str | None
    input: Any
    output: Any


class Test:
    called = []

    def __init__(self, file: str | Path) -> None:
        assert isinstance(file, Path) or isinstance(file, str)

        self._file = file if isinstance(file, Path) else Path(file)

        d = self._load_toml(self._file)
        self._parse(d)

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

    def _load_toml(self, file: str | Path) -> dict[str, Any]:
        with open(file, "rb") as file:
            return toml.load(file)

    def _parse(self, data: dict[str, Any]):
        print(data)
