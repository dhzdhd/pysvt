import inspect
import time
import tomllib as toml
from dataclasses import dataclass
from functools import wraps
from pathlib import Path
from typing import Any, Callable
import re

from rich.console import Console
from rich.status import Status

type Function = Callable[..., Any]

console = Console()


@dataclass(frozen=True)
class _Model:
    inputs: list[Any]
    output: Any
    name: str | None = None
    metadata: str | None = None


class ValidationError(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class test_cls:
    def __init__(self, file: str | Path, method: str) -> None:
        self._file = file
        self._method = method

    def __call__(self, cls: object) -> Any:
        # can use inspect too
        method = getattr(cls, self._method, None)
        if not callable(method):
            raise ValueError("Invalid method passed")
        # pass __init__ args through toml file - init/class key

        @wraps(cls)
        def wrapper(*args, **kwargs):
            return cls(*args, **kwargs)

        return wrapper


class test_fn:
    def __init__(
        self,
        file: str | Path,
        func: Function | None = None,
    ) -> None:
        if not (isinstance(file, Path) or isinstance(file, str)):
            raise ValueError("File type should be either str or Path")

        self._file = file if isinstance(file, Path) else Path(file)
        self._data: list[_Model] = []

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

    def _parse(self, data: dict[str, Any]):
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
                    print(output_key.string)
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
                    _Model(
                        inputs=inputs[i],
                        output=outputs[i],
                        metadata=metadata,
                        name=f"{name} [bold blue]{i + 1}[/bold blue]",
                    )
                )

    def _validate(self, func: Function):
        failures = 0

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
                    failures += 1
                else:
                    console.print(
                        f"\nTask [bold blue]{index + 1}[/bold blue] - [bold green]{data.name} complete\n\n"
                    )

            else:
                for o in self._outputs:
                    assert func() == o

        status = (
            "[bold green]SUCCESS[/bold green]"
            if failures == 0
            else "[bold red]FAILURE[/bold red]"
        )
        console.print(
            f"{status} | [bold green]{len(self._data) - failures} passed[/bold green] | [bold red]{failures} failed"
        )
