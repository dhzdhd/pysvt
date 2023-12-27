import pytest
from pysvt import test_cls, ValidationError
from tomllib import load


class Sample:
    def sample(self, a: int) -> int:
        return a


# def test_initialized_with_file_path_and_method_name():
#     file = "test.toml"
#     method = "test_method"
#     t = test_cls(file, method)
#     assert t._file == file
#     assert t._method == method
