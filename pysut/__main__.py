import inspect
import time
import tomllib as toml
from dataclasses import dataclass
from functools import wraps
from pathlib import Path
from typing import Any, Callable

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


# Perhaps make a decorator for an entire class with specified method to test
class Test:
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
        if not any(["o" in data, "outputs" in data, "data" in data]):
            raise ValidationError("Must contain one of o, outputs or data keys")

        inputs = []
        outputs = []
        metadata = "No metadata"
        name = "Test case"

        if "cases" in data:
            ...
        else:
            # Use regex to match o+, i+
            if any(["o" in data, "out" in data, "output" in data, "outputs" in data]):
                if any(["i" in data, "in" in data, "input" in data, "inputs" in data]):
                    inputs = data["i"]
                outputs = data["o"]
            else:
                raise ValidationError("No output data given")

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
