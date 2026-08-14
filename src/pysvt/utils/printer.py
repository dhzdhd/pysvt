"""Printer utility class to facilitate pretty printing."""

import inspect
from typing import final

from rich.console import Console
from rich.layout import Layout
from rich.panel import Panel
from rich.status import Status

from .models import FuncModel, Result


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

        input_title_str = f"""{Printer.bold("Input")} -"""
        input_str = "\n".join(map(lambda t: f"    {t[0]} - {t[1]}", zip(input_args, data.inputs)))
        input_str = "    None" if input_str.strip() == "" else input_str

        exp_out_str = f"""{Printer.bold("Expected output")} - {data.output}"""
        act_out_str = f"""{Printer.bold("Actual output")} - {res.data}"""

        out_str = f"{input_title_str}\n{input_str}\n{exp_out_str}\n{act_out_str}"

        if res.stdout is not None and res.stdout.strip() != "":
            out_str += f"""\n\n{Printer.bold("Stdout")} -\n{res.stdout.strip()}"""

        if res.local_vars is not None:
            out_str += f"""\n\n{Printer.bold("Local variables")} -"""

            for k, v in res.local_vars.items():
                out_str += f"\n    {k} - {v}"

        emoji = ":white_check_mark:" if res.valid else ":cross_mark:"
        time_str = f"{time_taken * 1000:.3f} ms" if time_taken < 1.0 else f"{time_taken:.3f} s"
        panel = Panel(
            out_str,
            title=f"{emoji}  {data.name}",
            subtitle=f"Time taken: {time_str}",
            subtitle_align="right",
        )

        if show_error_only and res.valid:
            self._console.print(panel)
            return
        self._console.print(panel)

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
