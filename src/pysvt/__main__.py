"""Main library class that contains all decorators."""

import inspect
import re
from contextlib import redirect_stdout
from copy import deepcopy
from functools import partial, wraps
from io import StringIO
from pathlib import Path
from typing import Any, Callable, ParamSpec, TypeVar, final

import tomllib as toml
from rich.console import Console

from pysvt.utils.ctx import Timer
from pysvt.utils.models import ClsModel, FuncModel, Result
from pysvt.utils.printer import Printer
from pysvt.utils.validation import get_result_locals

console = Console()
P = ParamSpec("P")
R = TypeVar("R")


class ValidationError(Exception):
    """Raise when validation of input data fails."""

    def __init__(self, *args: object) -> None:
        """Initialize Exception class with the same arguments."""
        super().__init__(*args)


@final
class test:
    """Decorator class for defining and running test cases.

    :param data: The test case data as a dictionary. Default is None.
    :param file: The path to the TOML file containing the test case data.
        Default is None.
    :param method: The name of the method to be tested (for class-based
        tests). Default is None.
    :param preprocess: A function to preprocess the test inputs. Default is
        None.
    :param postprocess: A function to postprocess the test outputs. Default
        is None.
    :param error_only: Flag indicating whether to display only the failed
        test cases. Default is False.
    :param pretty_print_errors: Flag indicating whether to pretty print
        errors with colors and more information. Default is True.
    :param redirect_stdout: Flag indicating whether to redirect all stdout
        (print statements, etc) to the pretty printed panels. Default is
        True.
    :param show_locals: Flag indicating whether to show local variable
        values after execution of the function. Default is False.
    :raises ValueError: If the `file` argument is not of type str or Path,
        or the `method` argument is not provided for instance methods.
    :raises ValidationError: If the decorator is applied incorrectly or the
        test case data is invalid.

    Usage:
    ```
    @test(file="data.toml")
    def function(arg1, arg2):
        # Your code

    @test(file="data.toml", method="method")
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
        pretty_print_errors: bool = True,
        redirect_stdout: bool = True,
        show_locals: bool = False,
    ) -> None:
        """Validate constructor arguments and initialize decorator state.

        :param data: The test case data as a dictionary.
        :param file: The path to the TOML file containing the test case
            data.
        :param method: The name of the method to be tested (for
            class-based tests).
        :param preprocess: A function to preprocess the test inputs.
        :param postprocess: A function to postprocess the test outputs.
        :param error_only: Whether to display only the failed test cases.
        :param pretty_print_errors: Whether to pretty print errors with
            colors and more information.
        :param redirect_stdout: Whether to redirect all stdout to the
            pretty printed panels.
        :param show_locals: Whether to show local variable values after
            execution of the function.
        :raises ValueError: If neither or both of `file`/`data` are
            provided, or `file` is not of type str or Path.
        """
        if (file is None and data is None) or (file is not None and data is not None):
            raise ValueError("Either of file or data argument should be filled")

        if file is not None:
            if not isinstance(file, (Path, str)):
                raise ValueError("File type should be either str or Path")

            self._raw = file if isinstance(file, Path) else Path(file)

        if data is not None:
            self._raw = data

        self._method = method
        self._preprocess = preprocess
        self._postprocess = postprocess
        self._show_error_only = error_only
        self._pretty_print_errors = pretty_print_errors
        self._redirect_stdout = redirect_stdout
        self._show_locals = show_locals

        self._printer = Printer(console)

        self._data: ClsModel | list[FuncModel] | None = None

    def __call__(self, obj: Callable[P, R]) -> Any:
        """Run the configured test cases against the decorated function or class.

        :param obj: The function or class being decorated.
        :return: A wrapper that forwards calls through to `obj` unchanged.
        :raises ValueError: If `obj` is a class and no `method` was
            provided to the decorator.
        :raises ValidationError: If the decorator is applied to the wrong
            kind of callable (e.g. an instance method used directly, or a
            non-instance method referenced via `method`).
        """
        is_class = inspect.isclass(obj)
        self._data = ClsModel([], []) if is_class else []

        self._parse(self._load_data())

        match self._data:
            case ClsModel():
                if self._method is None:
                    raise ValueError("method argument not provided")

                method = getattr(obj, self._method, None)

                if "self" not in method.__code__.co_varnames:
                    raise ValidationError(
                        "The decorator cannot be applied to non-instance methods. Instead, use it directly on the function"
                    )

                failures = 0

                for index, data in enumerate(self._data.data):
                    instance = obj(*self._data.init[index])
                    partial_method: partial[Any] = partial(method, instance)
                    with Timer() as timer:
                        result = self._validate(data, partial_method)
                    failures += 0 if result.valid else 1

                    self._printer.post_validation(
                        result, data, partial_method, timer(), self._show_error_only
                    )
                self._printer.finish(len(self._data.data), failures)
            case list():
                if "self" in obj.__code__.co_varnames:
                    raise ValidationError(
                        "The decorator cannot be applied to instance methods. Instead, apply it on the class and pass the name of the method as an argument"
                    )

                failures = 0

                for index, data in enumerate(self._data):
                    with Timer() as timer:
                        result = self._validate(data, obj)
                    failures += 0 if result.valid else 1

                    self._printer.post_validation(result, data, obj, timer(), self._show_error_only)

                self._printer.finish(len(self._data), failures)

        @wraps(obj)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            return obj(*args, **kwargs)

        return wrapper

    def _load_data(self) -> dict[str, Any]:
        """Load test case data from a TOML file, or return it directly.

        :return: The test case data as a dictionary, either loaded from
            the configured TOML file or passed through as-is.
        :raises FileNotFoundError: If the specified file does not exist.
        :raises tomllib.TOMLDecodeError: If the TOML file is not valid.
        """
        if isinstance(self._raw, Path):
            with open(self._raw, "rb") as f:
                return toml.load(f)
        else:
            return self._raw

    def _parse(self, data: dict[str, Any]) -> None:
        """Parse test case data and populate the `ClsModel`/`FuncModel` state.

        :param data: The test case data loaded from the TOML file or
            passed directly.
        :param is_class: Whether the test is class-based or
            function-based.
        :raises ValidationError: If the test case data is invalid (e.g.
            missing output data, or mismatched input/output/init lengths).
        """
        inputs: list[Any] = []
        outputs: list[Any] = []
        metadata: list[str] = []
        name: list[str] = []
        init: list[Any] = []

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
            output_exists = None

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

        if self._data is not None:
            if isinstance(self._data, ClsModel):
                self._data.init = init

            for i in range(len(outputs)):
                _input = inputs[i] if self._preprocess is None else self._preprocess(inputs[i])
                func_model = FuncModel(
                    inputs=_input,
                    output=outputs[i],
                    metadata=metadata[i],
                    name=f"{name[i]} {Printer.number(i + 1)}",
                )

                match self._data:
                    case ClsModel():
                        self._data.data.append(func_model)
                    case list():
                        self._data.append(func_model)

    def _validate(self, data: FuncModel, func: Callable[..., Any]) -> Result:
        """Execute a test case and compare the result with the expected output.

        :param data: The test case data.
        :param func: The test function to be executed.
        :return: The validation result, including the actual result and a
            flag indicating whether the test passed or failed.
        :raises ValidationError: If the test case inputs are not nested
            within a list.
        """
        partial_fn = partial(func)
        stdout = None
        local_vars = None
        result = None

        if not isinstance(data.inputs, list):
            raise ValidationError("Inputs must be nested within a list")
        # deepcopy to avoid inconsistent inputs being printed due to mutations
        partial_fn = partial(func, *deepcopy(data.inputs))

        if self._pretty_print_errors:
            try:
                if self._redirect_stdout:
                    with redirect_stdout(StringIO()) as f:
                        if self._show_locals:
                            result, local_vars = get_result_locals(partial_fn)
                        else:
                            result = partial_fn()
                    stdout = f.getvalue()
                else:
                    if self._show_locals:
                        result, local_vars = get_result_locals(partial_fn)
                    else:
                        result = partial_fn()
            except Exception:
                console.print_exception(show_locals=True)
        else:
            if self._redirect_stdout:
                with redirect_stdout(StringIO()) as f:
                    if self._show_locals:
                        result, local_vars = get_result_locals(partial_fn)
                    else:
                        result = partial_fn()
                stdout = f.getvalue()
            else:
                if self._show_locals:
                    result, local_vars = get_result_locals(partial_fn)
                else:
                    result = partial_fn()

        if self._postprocess is not None:
            result = self._postprocess(result)

        return Result(result, stdout, result == data.output, local_vars)
