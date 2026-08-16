"""Printer utility class to facilitate pretty printing."""

import inspect
from typing import final

from rich.console import Console, Group, RenderableType
from rich.layout import Layout
from rich.panel import Panel
from rich.status import Status
from rich.table import Table

from .models import FuncModel, Result, Variable


@final
class Printer:
    """Provide utility methods for printing and displaying information during testing.

    :param console: The console object used for printing.
    """

    def __init__(self, console: Console) -> None:
        """Initialize the printer with a console instance.

        :param console: The console object used for printing.
        """
        self._console = console
        self._layout = Layout()

    def init(self) -> Status:
        """Initialize the printer in normal mode.

        :return: The status of the initialization process.
        """
        return Status("Running tests")

    def post_validation(
        self,
        res: Result,
        data: FuncModel,
        obj: object,
        time_taken: float,
        show_error_only: bool,
    ) -> None:
        """Print the result of a validation in a formatted panel.

        :param res: The validation result.
        :param data: The function model containing input, expected output,
            and name.
        :param obj: The function on which the decorator was applied.
        :param time_taken: The time taken for the validation.
        :param show_error_only: Flag indicating whether to show only the
            error panel.
        """
        input_args = inspect.getfullargspec(obj).args

        input_str = "\n".join(map(lambda t: f"    {t[0]} - {t[1]}", zip(input_args, data.inputs)))
        input_str = "None" if input_str.strip() == "" else input_str

        emoji = ":white_check_mark:" if res.valid else ":cross_mark:"
        time_str = f"{time_taken * 1000:.3f} ms" if time_taken < 1.0 else f"{time_taken:.3f} s"

        output_layout = Layout()
        output_layout.split_row(
            Layout(Panel(str(data.output), title="Expected output", style="dim"), ratio=1),
            Layout(Panel(str(res.data), title="Actual output", style="dim"), ratio=1),
        )

        panels: list[RenderableType] = []
        panels.append(Panel(input_str, title="Input", style="dim"))
        panels.append(output_layout)
        if res.stdout is not None and res.stdout.strip() != "":
            panels.append(Panel(res.stdout.strip(), title="Stdout", style="dim"))
        if res.local_vars:
            panels.append(self.variable_table(res.local_vars))

        element_group = Group(*panels)

        panel = Panel(
            element_group,
            title=f"{emoji}  {data.name}",
            subtitle=f"Time taken: {time_str}",
            subtitle_align="right",
        )

        if show_error_only and res.valid:
            self._console.print(panel)
            return
        self._console.print(panel)

    def variable_table(self, local_vars: list[Variable]) -> Table:
        """Create a table displaying local variables from execution frames.

        :param local_vars: List of Variable objects containing frame data.
        :return: A Rich Table with columns for frame index, variable names,
            values, line numbers, and source code.
        """
        table = Table(title="Local variables", style="dim", expand=True)
        table.add_column("Frame", style="dim")
        table.add_column("Variable")
        table.add_column("Value")
        table.add_column("Line number")
        table.add_column("Code")

        for idx, var in enumerate(local_vars):
            table.add_row(
                str(idx),
                "\n".join(var.names),
                "\n".join(map(str, var.values)),
                str(var.line_number),
                var.code,
            )
            table.add_section()

        return table

    def finish(self, total: int, failures: int) -> None:
        """Print the final test execution summary.

        :param total: The total number of tests executed.
        :param failures: The number of tests that failed.
        """
        success = Printer.success(f"{total - failures} passed")
        failure = Printer.error(f"{failures} failed")

        status = Printer.success("SUCCESS") if failures == 0 else Printer.error("FAILURE")
        self._console.print(f"{status} | {success} | {failure}")

    def traceback(self):
        """Print the traceback of an exception, including local variables."""
        self._console.print_exception(show_locals=True)

    @staticmethod
    def bold(data: str) -> str:
        """Format the given data in bold font weight.

        :param data: The data to be formatted.
        :return: The formatted message.
        """
        return f"[bold]{data}[/bold]"

    @staticmethod
    def success(data: str) -> str:
        """Format the given data as a success message.

        :param data: The data to be formatted.
        :return: The formatted success message.
        """
        return f"[bold green]{data}[/bold green]"

    @staticmethod
    def error(data: str) -> str:
        """Format the given data as an error message.

        :param data: The error message to format.
        :return: The formatted error message.
        """
        return f"[bold red]{data}[/bold red]"

    @staticmethod
    def number(data: int) -> str:
        """Format the given integer as a string with bold blue color.

        :param data: The integer to be formatted.
        :return: The formatted string.
        """
        return f"[bold blue]{data}[/bold blue]"
