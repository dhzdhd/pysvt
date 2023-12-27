"""
This module contains the `test` decorator class and supporting functions for validating test cases.

Classes:
- `ValidationError`: Custom exception class for validation errors.
- `test`: Decorator class for defining and running test cases.

Functions:
- `_load_file`: Loads a TOML file and returns its contents as a dictionary.
- `_parse`: Parses the test case data from the TOML file and populates the `_ClsModel` or `_FuncModel` objects.
- `_validate`: Validates a test case by executing the test function and comparing the result with the expected output.
"""

import inspect
import time
import tomllib as toml
from functools import wraps, partial
from pathlib import Path
from typing import Any, Callable
import re
from pysut.utils.printer import Printer
from pysut.utils.models import _ClsModel, _FuncModel, Result
from pysut.utils.ctx import Timer
from rich.console import Console

type Function = Callable[..., Any]

console = Console()


class ValidationError(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class test:
    """
    Decorator class for defining and running test cases.

    Args:
    - `file` (str or Path): The path to the TOML file containing the test case data.
    - `method` (str or None): The name of the method to be tested (for class-based tests). Default is None.
    - `error_only` (bool): Flag indicating whether to display only the failed test cases. Default is False.

    Raises:
    - `ValueError`: If the `file` argument is not of type str or Path or `method` argument is not provided for instance methods.
    - `ValidationError`: If the decorator is applied incorrectly or the test case data is invalid.

    Usage:
    ```
    @test("data.toml")
    def test_function(input, expected_output):
        # Test implementation

    @test("data.toml", method="test_method")
    class TestClass:
        def test_method(self, input, expected_output):
            # Test implementation
    ```
    """

    def __init__(
        self, file: str | Path, method: str | None = None, error_only: bool = False
    ) -> None:
        if not (isinstance(file, Path) or isinstance(file, str)):
            raise ValueError("File type should be either str or Path")

        self._file = file if isinstance(file, Path) else Path(file)
        self._method = method
        self._show_error_only = error_only

        self._printer = Printer(console)

        self._data: _ClsModel | list[_FuncModel] | None = None

    def __call__(self, obj: object) -> Any:
        is_class = inspect.isclass(obj)
        self._data = _ClsModel([], []) if is_class else []

        self._parse(self._load_file(), is_class)

        if is_class:
            if self._method is None:
                raise ValueError("method argument not provided")

            method = getattr(obj, self._method, None)

            if "self" not in method.__code__.co_varnames:
                raise ValidationError(
                    "The decorator cannot be applied to non-instance methods. Instead, use it directly on the function"
                )

            with self._printer.init(self._data.data) as _:
                failures = 0

                for index, data in enumerate(self._data.data):
                    self._printer.pre_validation(index, data)

                    partial_method = partial(method, obj(*self._data.init[index]))
                    with Timer() as timer:
                        result = self._validate(data, partial_method)
                    failures += 0 if result.valid else 1

                    self._printer.post_validation(
                        result, data.name, timer(), self._show_error_only
                    )

            self._printer.finish(len(self._data.data), failures)
        else:
            if "self" in obj.__code__.co_varnames:
                raise ValidationError(
                    "The decorator cannot be applied to instance methods. Instead, apply it on the class and pass the name of the method as an argument"
                )

            with self._printer.init(self._data) as _:
                failures = 0

                for index, data in enumerate(self._data):
                    self._printer.pre_validation(index, data)

                    result = self._validate(data, obj)
                    failures += 0 if result.valid else 1

                    self._printer.post_validation(
                        result, data.name, self._show_error_only
                    )

            self._printer.finish(len(self._data), failures)

        @wraps(obj)
        def wrapper(*args, **kwargs):
            return obj(*args, **kwargs)

        return wrapper

    def _load_file(self) -> dict[str, Any]:
        """
        Loads a TOML file and returns its contents as a dictionary.

        Returns:
        - dict: The contents of the TOML file.

        Raises:
        - FileNotFoundError: If the specified file does not exist.
        - tomllib.TomlDecodeError: If the TOML file is not valid.
        """
        with open(self._file, "rb") as f:
            return toml.load(f)

    def _parse(self, data: dict[str, Any], is_class: bool) -> None:
        """
        Parses the test case data from the TOML file and populates the `_ClsModel` or `_FuncModel` objects.

        Args:
        - `data` (dict): The test case data loaded from the TOML file.
        - `is_class` (bool): Flag indicating whether the test is class-based or function-based.

        Raises:
        - `ValidationError`: If the test case data is invalid.
        """
        inputs = []
        outputs = []
        metadata = []
        name = []
        init = []

        output_re = re.compile(r"^o(?:ut|utput|utputs)?$")
        input_re = re.compile(r"^i(?:n|nput|nputs)?$")

        if "cases" in data:
            for case in data["cases"]:
                for key in case.keys():
                    output_key = output_re.match(key)

                    if output_key is not None:
                        outputs.append(case[output_key.string])
                        break

                for key in case.keys():
                    input_key = input_re.match(key)

                    if input_key is not None:
                        inputs.append(case[input_key.string])
                        break

                if "metadata" in case:
                    metadata.append(case["metadata"])

                if "name" in case:
                    name.append(case["name"])

                if "init" in case:
                    init.append(case["init"])
        else:
            for key in data.keys():
                output_key = output_re.match(key)

                if output_key is not None:
                    output_exists = True
                    outputs = data[output_key.string]
                    break

            for key in data.keys():
                input_key = input_re.match(key)

                if input_key is not None:
                    inputs = data[input_key.string]
                    break

            if not output_exists:
                raise ValidationError("No output data given or output key is invalid")

            if "metadata" in data:
                if isinstance(data["metadata"], list):
                    metadata = data["metadata"]
                else:
                    metadata = [data["metadata"] for _ in range(len(outputs))]

            if "name" in data:
                if isinstance(data["name"], list):
                    name = data["name"]
                else:
                    name = [data["name"] for _ in range(len(outputs))]

            if "init" in data:
                if isinstance(data["init"], list):
                    init = data["init"]
                else:
                    init = [data["init"] for _ in range(len(outputs))]

        if outputs == []:
            raise ValidationError("No output data given or output key is invalid")

        if inputs != [] and len(inputs) != len(outputs):
            raise ValidationError("Input and output data are not of the same length")

        if init != [] and len(outputs) != len(init):
            raise ValidationError("Init and output data are not of the same length")

        if init == []:
            init = [[] for _ in range(len(outputs))]
        while len(outputs) != len(metadata):
            metadata.append("No metadata")
        while len(outputs) != len(name):
            name.append("Test case")

        if is_class:
            self._data.init = init

        for i in range(len(outputs)):
            func_model = _FuncModel(
                inputs=inputs[i],
                output=outputs[i],
                metadata=metadata[i],
                name=f"{name[i]} {Printer.number(i + 1)}",
            )

            if is_class:
                self._data.data.append(func_model)
            else:
                self._data.append(func_model)

    def _validate(self, data: _FuncModel, func: Function) -> Result:
        """
        Validates a test case by executing the test function and comparing the result with the expected output.

        Args:
        - `data` (_FuncModel): The test case data.
        - `func` (Function): The test function to be executed.

        Returns:
        - Result: The validation result, including the actual result and a flag indicating whether the test passed or failed.

        Raises:
        - `ValidationError`: If the test case inputs are not of the expected format.
        """
        if data.inputs is not None:
            if not isinstance(data.inputs, list):
                raise ValidationError("Inputs must be nested within a list")

            result = func(*data.inputs)
        else:
            result = func()

        return Result(result, result == data.output)
