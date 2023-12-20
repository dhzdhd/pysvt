from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class _FuncModel:
    inputs: list[Any]
    output: Any
    name: str | None = None
    metadata: str | None = None


@dataclass()
class _ClsModel:
    init: list[Any]
    data: list[_FuncModel]


@dataclass(frozen=True)
class Result[T]:
    data: T
    valid: bool
