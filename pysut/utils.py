from pathlib import Path
from tomllib import load

from typing import Any


def load_toml(file: str | Path):
    with open(file, "rb") as file:
        return load(file)


def parse(data: dict[str, Any]):
    print(data)
