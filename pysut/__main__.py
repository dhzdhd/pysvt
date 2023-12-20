import inspect
import time
import tomllib as toml
from functools import wraps, partial
from pathlib import Path
from typing import Any, Callable
import re
from pysut.utils.printer import Printer
from pysut.utils.models import _ClsModel, _FuncModel, Result
from rich.console import Console

type Function = Callable[..., Any]

console = Console()


class ValidationError(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class test_cls:
    def __init__(self, file: str | Path, method: str) -> None:
        if not (isinstance(file, Path) or isinstance(file, str)):
            raise ValueError("File type should be either str or Path")

        self._file = file if isinstance(file, Path) else Path(file)
        self._method = method

        self._printer = Printer(console)

        self._data: _ClsModel = _ClsModel([], [])
        self.failures = 0

        self._parse(self._load_toml(self._file))

    def __call__(self, cls: object) -> Any:
        if not inspect.isclass(cls):
            raise ValueError("The decorator cannot be applied on classes")

        method = getattr(cls, self._method, None)

        if not inspect.isfunction(method):
            raise ValueError("Invalid method passed")
        else:
            partial_method = partial(method, cls(*self._data.init))

        if "self" in method.__code__.co_varnames:
            with self._printer.init() as status:
                for index, data in enumerate(self._data.data):
                    self._printer.pre_validation(data)

                    result = self._validate(index, data, partial_method)
                    self.failures += 0 if result.valid else 1

                    self._printer.post_validation(result.data)

                self._printer.finish(len(self._data.data), self.failures)

        else:
            raise ValidationError(
                "The decorator cannot be applied to non-instance methods"
            )

        @wraps(cls)
        def wrapper(*args, **kwargs):
            return cls(*args, **kwargs)

        return wrapper

    def _load_toml(self, file: str | Path) -> dict[str, Any]:
        with open(file, "rb") as file:
            return toml.load(file)

    def _parse(self, data: dict[str, Any]) -> None:
        inputs = []
        outputs = []
        metadata = "No metadata"
        name = "Test case"
        init = []

        output_re = re.compile(r"^o(?:ut|utput|utputs)?$")
        input_re = re.compile(r"^i(?:n|nput|nputs)?$")

        if "cases" in data:
            ...
        else:
            output_exists = False
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
                metadata = data["metadata"]

            if "name" in data:
                name = data["name"]

            if "init" in data:
                init = data["init"]

            if len(inputs) != len(outputs):
                raise ValidationError(
                    "Input and output data are not of the same length"
                )

            for i in range(len(outputs)):
                self._data.data.append(
                    _FuncModel(
                        inputs=inputs[i],
                        output=outputs[i],
                        metadata=metadata,
                        name=f"{name} {Printer.number(i + 1)}",
                    )
                )
            self._data.init = init

    def _validate[T](self, index: int, data: _FuncModel, func: Function) -> Result[T]:
        if data.inputs is not None:
            if not isinstance(data.inputs, list):
                raise ValidationError("Inputs must be nested within a list")

            result = func(*data.inputs)
            # console.print(f"Actual output - {result}")

            # if result != data.output:
            # console.print(
            #     f"\nTask [bold blue]{index + 1}[/bold blue] - [bold red]{data.name} failed\n\n"
            # )
            # self.failures += 1
            # else:
            # instead of printing, return result
            # console.print(
            #    f"\nTask [bold blue]{index + 1}[/bold blue] - [bold green]{data.name} complete\n\n"
            # )

        else:
            result = func()

        return Result(result, result != data.output)


class test_fn:
    def __init__(
        self,
        file: str | Path,
        func: Function | None = None,
    ) -> None:
        if not (isinstance(file, Path) or isinstance(file, str)):
            raise ValueError("File type should be either str or Path")

        self._file = file if isinstance(file, Path) else Path(file)
        self._data: list[_FuncModel] = []

        self._parse(self._load_toml(self._file))

        if func is not None:
            if inspect.isfunction(func):
                self._validate(func)
            else:
                raise ValueError("func argument is not a function")

    def __call__(self, func: Function) -> Any:
        if inspect.isclass(func):
            raise ValueError("The decorator cannot be applied on classes")
        else:
            if "self" in func.__code__.co_varnames:
                raise ValidationError(
                    "The decorator cannot be applied to instance methods"
                )
            else:
                with console.status("[bold green] Running tests...") as status:
                    self._validate(func)

        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        return wrapper

    def _load_toml(self, file: str | Path) -> dict[str, Any]:
        with open(file, "rb") as file:
            return toml.load(file)

    def _parse(self, data: dict[str, Any]) -> None:
        inputs = []
        outputs = []
        metadata = "No metadata"
        name = "Test case"

        # Move printing to another fn
        if "cases" in data:
            ...
        else:
            output_re = re.compile(r"^o(?:ut|utput|utputs)?$")
            input_re = re.compile(r"^i(?:n|nput|nputs)?$")

            output_exists = False
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
                metadata = data["metadata"]

            if "name" in data:
                name = data["name"]

            if len(inputs) != len(outputs):
                raise ValidationError(
                    "Input and output data are not of the same length"
                )

            for i in range(len(outputs)):
                self._data.append(
                    _FuncModel(
                        inputs=inputs[i],
                        output=outputs[i],
                        metadata=metadata,
                        name=f"{name} [bold blue]{i + 1}[/bold blue]",
                    )
                )

    def _validate(self, func: Function):
        self.failures = 0

        for index, data in enumerate(self._data):
            if data.inputs is not None:
                if not isinstance(data.inputs, list):
                    raise ValidationError("Inputs must be nested within a list")

                console.print(f"Input - {data.inputs}")
                console.print(f"Expected output - {data.output}")

                result = func(*data.inputs)
                console.print(f"Actual output - {result}")

                if result != data.output:
                    console.print(
                        f"\nTask [bold blue]{index + 1}[/bold blue] - [bold red]{data.name} failed\n\n"
                    )
                    self.failures += 1
                else:
                    console.print(
                        f"\nTask [bold blue]{index + 1}[/bold blue] - [bold green]{data.name} complete\n\n"
                    )

            else:
                for o in self._outputs:
                    assert func() == o

        status = (
            "[bold green]SUCCESS[/bold green]"
            if self.failures == 0
            else "[bold red]FAILURE[/bold red]"
        )
        console.print(
            f"{status} | [bold green]{len(self._data) - self.failures} passed[/bold green] | [bold red]{self.failures} failed"
        )
