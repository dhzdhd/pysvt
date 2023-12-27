import pytest
from pysvt import test_fn, ValidationError
import json
import tomllib


def sample(a: int) -> int:
    return a


class Sample:
    def sample(self, a: int) -> int:
        return a


def test_incorrect_toml_file():
    with pytest.raises(FileNotFoundError):
        test_fn("tests/inputt.toml")(sample)


def test_invalid_file_entry_type():
    with pytest.raises(ValueError):
        test_fn(5)(sample)


def test_instance_methods():
    with pytest.raises(ValueError):
        test_fn(5)(Sample.sample)


def test_incorrect_output_key():
    with pytest.raises(ValidationError):
        sample = test_fn("tests/data/func_incorrect.toml")(sample)


def _load_toml(file):
    with open(file, "rb") as f:
        return tomllib.load(f)


def test_load_fn():
    with open("tests/data/output.json", "w") as f:
        o1 = _load_toml("tests/data/input.toml")
        o2 = _load_toml("tests/data/cases.toml")

        o = [o1, o2]
        json.dump(o, f)
