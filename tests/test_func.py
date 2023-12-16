import pytest
from pysut import test_fn, ValidationError


def sample(a: int) -> int:
    return a


class Sample:
    def sample(self, a: int) -> int:
        return a


def test_incorrect_toml_file():
    with pytest.raises(FileNotFoundError):
        sample = test_fn("tests/inputt.toml")(sample)


def test_invalid_file_entry_type():
    with pytest.raises(ValueError):
        sample = test_fn(5)(sample)


def test_instance_methods():
    with pytest.raises(ValueError):
        Sample.sample = test_fn(5)(Sample.sample)


def test_incorrect_output_key():
    with pytest.raises(ValidationError):
        sample = test_fn("tests/data/func_incorrect.toml")(sample)
