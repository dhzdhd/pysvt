import inspect
import re
import tomllib as toml
from contextlib import redirect_stdout
from copy import deepcopy
from functools import partial, wraps
from io import StringIO
from pathlib import Path
from typing import Any, Callable

from rich.console import Console

from pysvt.utils.ctx import Timer
from pysvt.utils.models import Result, _ClsModel, _FuncModel
from pysvt.utils.printer import Printer

console = Console()


class ValidationError(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class test:
    """
    Decorator class for defining and running test cases.

    Args:
    - `file` (str or Path): The path to the TOML file containing the test case data. Default is None.
    - `data` (dict[str, Any]): The test case data as a dictionary. Default is None.
    - `method` (str or None): The name of the method to be tested (for class-based tests). Default is None.
    - `preprocess` (Callable[..., Any] or None): A function to preprocess the test inputs. Default is None.
    - `postprocess` (Callable[..., Any] or None): A function to postprocess the test outputs. Default is None.
    - `error_only` (bool): Flag indicating whether to display only the failed test cases. Default is False.
    - `is_live` (bool): Flag indicating whether to run the tests in live mode. Default is False.
    - `pretty_print_errors` (bool): Flag indicating whether to pretty print errors with colors and more information. Default is True.
    - `redirect_stdout` (bool): Flag indicating whether to redirect all stdout (print statements, etc) to the pretty printed panels. Default is True.
    - `show_locals` (bool): Flag indicating whether to show local variable values after execution of the function. Default is False.

    Raises:
    - `ValueError`: If the `file` argument is not of type str or Path or `method` argument is not provided for instance methods.
    - `ValidationError`: If the decorator is applied incorrectly or the test case data is invalid.

    Usage:
    ```
    @test("data.toml")
    def function(arg1, arg2):
        # Your code

    @test("data.toml", method="method")
    class Demo:
        def method(self, arg1, arg2):
            # Your code

    data = {
        "i": [[1, 2], [2, 3]],
        "o": [2, 3],
    }
    @test(data=data)
    def function(arg1, arg2):
        # Your code
    ```
    """

    def __init__(
        self,
        data: dict[str, Any] | None = None,
        file: str | Path | None = None,
        method: str | None = None,
        preprocess: Callable[..., Any] | None = None,
        postprocess: Callable[..., Any] | None = None,
        error_only: bool = False,
        is_live: bool = False,
        pretty_print_errors: bool = True,
        redirect_stdout: bool = True,
        show_locals: bool = False,
    ) -> None:
        if show_locals:
            raise NotImplementedError("show_locals has not been implemented yet")

        if (file is None and data is None) or (file is not None and data is not None):
            raise ValueError("Either of file or data argument should be filled")

        if file is not None:
            if not (isinstance(file, Path) or isinstance(file, str)):
                raise ValueError("File type should be either str or Path")

            self._raw = file if isinstance(file, Path) else Path(file)

        if data is not None:
            self._raw = data

        self._method = method
        self._preprocess = preprocess
        self._postprocess = postprocess
        self._show_error_only = error_only
        self._is_live = is_live
        self._pretty_print_errors = pretty_print_errors
        self._redirect_stdout = redirect_stdout
        self._show_locals = show_locals

        self._printer = Printer(console, self._is_live)

        self._data: _ClsModel | list[_FuncModel] | None = None

    def __call__(self, obj: object) -> Any:
        is_class = inspect.isclass(obj)
        self._data = _ClsModel([], []) if is_class else []

        self._parse(self._load_data(), is_class)

        if is_class:
            if self._method is None:
                raise ValueError("method argument not provided")

            method = getattr(obj, self._method, None)

            if "self" not in method.__code__.co_varnames:
                raise ValidationError(
                    "The decorator cannot be applied to non-instance methods. Instead, use it directly on the function"
                )

            if self._is_live:
                with self._printer.init_live(self._data.data) as _:
                    failures = 0

                    for index, data in enumerate(self._data.data):
                        self._printer.pre_validation(data)

                        partial_method = partial(method, obj(*self._data.init[index]))
                        with Timer() as timer:
                            result = self._validate(data, partial_method)
                        failures += 0 if result.valid else 1

                        self._printer.post_validation(
                            result, data.name, timer(), self._show_error_only
                        )

                self._printer.clean_up()
                self._printer.finish(len(self._data.data), failures)
            else:
                # with self._printer.init_normal() as _:
                failures = 0

                for index, data in enumerate(self._data.data):
                    partial_method = partial(method, obj(*self._data.init[index]))
                    with Timer() as timer:
                        result = self._validate(data, partial_method)
                    failures += 0 if result.valid else 1

                    self._printer.post_validation_normal(
                        result, data, timer(), self._show_error_only
                    )
                self._printer.finish(len(self._data.data), failures)
        else:
            if "self" in obj.__code__.co_varnames:
                raise ValidationError(
                    "The decorator cannot be applied to instance methods. Instead, apply it on the class and pass the name of the method as an argument"
                )

            if self._is_live:
                with self._printer.init_live(self._data) as _:
                    failures = 0

                    for index, data in enumerate(self._data):
                        self._printer.pre_validation(data)

                        with Timer() as timer:
                            result = self._validate(data, obj)
                        failures += 0 if result.valid else 1

                        self._printer.post_validation(
                            result, data.name, timer(), self._show_error_only
                        )

                self._printer.clean_up()
                self._printer.finish(len(self._data), failures)
            else:
                # with self._printer.init_normal() as _:
                failures = 0

                for index, data in enumerate(self._data):
                    with Timer() as timer:
                        result = self._validate(data, obj)
                    failures += 0 if result.valid else 1

                    self._printer.post_validation_normal(
                        result, data, timer(), self._show_error_only
                    )

                self._printer.finish(len(self._data), failures)

        @wraps(obj)
        def wrapper(*args, **kwargs):
            return obj(*args, **kwargs)

        return wrapper

    def _load_data(self) -> dict[str, Any]:
        """
        Loads a TOML file and returns its contents as a dictionary.

        Returns:
        - dict: The contents of the TOML file.

        Raises:
        - FileNotFoundError: If the specified file does not exist.
        - tomllib.TomlDecodeError: If the TOML file is not valid.
        """
        if isinstance(self._raw, Path):
            with open(self._raw, "rb") as f:
                return toml.load(f)
        else:
            return self._raw

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
            _input = (
                inputs[i] if self._preprocess is None else self._preprocess(inputs[i])
            )
            func_model = _FuncModel(
                inputs=_input,
                output=outputs[i],
                metadata=metadata[i],
                name=f"{name[i]} {Printer.number(i + 1)}",
            )

            if is_class:
                self._data.data.append(func_model)
            else:
                self._data.append(func_model)

    def _validate(self, data: _FuncModel, func: Callable[..., Any]) -> Result:
        """
        Validates a test case by executing the test function and comparing the result with the expected output.

        Args:
        - `data` (_FuncModel): The test case data.
        - `func` (Callable[..., Any]): The test function to be executed.

        Returns:
        - Result: The validation result, including the actual result and a flag indicating whether the test passed or failed.

        Raises:
        - `ValidationError`: If the test case inputs are not of the expected format.
        """
        partial_fn = partial(func)
        stdout = None

        if data.inputs is not None:
            if not isinstance(data.inputs, list):
                raise ValidationError("Inputs must be nested within a list")
            # deepcopy to avoid inconsistent inputs being printed due to mutations
            partial_fn = partial(func, *deepcopy(data.inputs))

        if self._pretty_print_errors:
            try:
                if self._redirect_stdout:
                    with redirect_stdout(StringIO()) as f:
                        result = partial_fn()
                    stdout = f.getvalue()
                else:
                    result = partial_fn()
            except Exception:
                console.print_exception(show_locals=True)
        else:
            if self._redirect_stdout:
                with redirect_stdout(StringIO()) as f:
                    result = partial_fn()
                stdout = f.getvalue()
            else:
                result = partial_fn()
        # else:
        #     if self._pretty_print_errors:
        #         try:
        #             result = func()
        #         except:
        #             console.print_exception(show_locals=True)
        #     else:
        #         result = func()

        if self._postprocess is not None:
            result = self._postprocess(result)

        return Result(result, stdout, result == data.output)


class inspect_locals:
    def __init__(self) -> None:
        ...

    def __call__(self, obj: object) -> Any:
        ...
