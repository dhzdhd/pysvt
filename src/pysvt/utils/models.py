"""Model utility class to provide data models for the library."""

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class FuncModel:
    """A single test case for a function-based test.

    :param inputs: The positional input arguments for the test case.
    :param output: The expected output for the test case.
    :param name: The display name of the test case.
    :param metadata: Additional metadata associated with the test case.
    """

    inputs: list[Any]
    output: Any
    name: str
    metadata: str


@dataclass()
class ClsModel:
    """Container for class-based test cases and their init arguments.

    :param init: The positional arguments used to construct an instance
        of the class under test, one entry per test case.
    :param data: The individual test cases to run against each
        constructed instance.
    """

    init: list[Any]
    data: list[FuncModel]


@dataclass(frozen=True)
class Result:
    """The outcome of validating a single test case.

    :param data: The actual value returned by the tested function.
    :param stdout: Captured stdout output from the test run, or `None` if
        stdout was not redirected.
    :param valid: Whether the actual output matched the expected output.
    :param local_vars: Captured local variables from the test run, or
        `None` if locals were not captured.
    """

    data: Any
    stdout: str | None
    valid: bool
    local_vars: dict[str, Any] | None
