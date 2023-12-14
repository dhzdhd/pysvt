from pathlib import Path
from tomllib import load


def load_toml(file: str | Path):
    with open(file, "rb") as file:
        return load(file)
