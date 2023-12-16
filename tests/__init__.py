import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from pysut import test_fn


class FuncTester(unittest.TestCase):
    def setUp(self):
        self.func = MagicMock()
        self.file = "tests/input.toml"
        self.tester = test_fn(self.func, self.file)

    @patch("tomllib.load")
    def test_parse_toml(self, mock_load):
        mock_load.return_value = {"key": "value"}

    # def test_call(self):
    #     self.tester("arg1", "arg2", kwarg1="kwarg1")
    #     self.func.assert_called_once_with("arg1", "arg2", kwarg1="kwarg1")


if __name__ == "__main__":
    unittest.main()
