from rich import print
from rich.console import Console
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.status import Status

from .models import Result, _FuncModel


class Printer:
    """
    A class that provides utility methods for printing and displaying information during testing.

    Args:
        console (Console): The console object used for printing.
        is_live (bool): A flag indicating whether the printer is in live mode or not.

    Methods:
        init_live(data: list[_FuncModel]) -> Live:
            Initializes the printer in live mode and returns the live object.

        init_normal() -> Status:
            Initializes the printer in normal mode and returns the status object.

        pre_validation(index: int, data: _FuncModel) -> None:
            Updates the information for a specific test case before validation.

        post_validation(res: Result, title: str, time_taken: float, show_error_only: bool) -> None:
            Updates the information after validating a test case.

        post_validation_normal(res: Result, data: _FuncModel, time_taken: float, show_error_only: bool) -> None:
            Updates the information after validating a test case in normal mode.

        clean_up() -> None:
            Cleans up the printer by clearing the console and stopping the live object.

        finish(total: int, failures: int) -> None:
            Prints the final test results.

        traceback() -> None:
            Prints the traceback of an exception.

        success(data: str) -> str:
            Formats the given data as a success message.

        error(data: str) -> str:
            Formats the given data as an error message.

        number(data: int) -> str:
            Formats the given data as a number message.
    """

    def __init__(self, console: Console, is_live: bool) -> None:
        self._console = console
        self._is_live = is_live
        self._layout = Layout()

    def init_live(self, data: list[_FuncModel]) -> Live:
        """
        Initializes and returns a Live object for displaying data.

        Args:
            data (list[_FuncModel]): A list of _FuncModel objects containing data to be displayed.

        Returns:
            Live: The initialized Live object.
        """
        for item in data:
            child = Layout(
                Panel(item.name, title=item.name),
                name=item.name,
            )
            self._layout.add_split(child)

        self._console.clear(True)

        self._live = Live(
            self._layout,
            console=self._console,
            refresh_per_second=10,
            # Turn off and transient=False to avoid printing again
            screen=True,
            vertical_overflow="visible",
        )
        return self._live

    def init_normal(self) -> Status:
        """
        Initializes the printer in normal mode.

        Returns:
            Status: The status of the initialization process.
        """
        return Status("Running tests")

    def pre_validation(self, data: _FuncModel) -> None:
        """
        Performs pre-validation for the given data.

        Args:
            data (_FuncModel): The data to be validated.
        """
        child = next(filter(lambda x: x.name == data.name, self._layout.children))

        string = f"Input - {data.inputs}\nExpected output - {data.output}"
        child.update(Panel(string, title=data.name))

    def post_validation(
        self, res: Result, title: str, time_taken: float, show_error_only: bool
    ) -> None:
        """
        Update the display panel with the result of the validation.

        Args:
            res (Result): The validation result.
            title (str): The title of the panel to update.
            time_taken (float): The time taken for the validation.
            show_error_only (bool): Flag indicating whether to show only error panels.
        """
        child = next(filter(lambda x: x.name == title, self._layout.children))
        panel: Panel = child.renderable

        out_str = f"{str(panel.renderable)}\nActual output - {res.data}"
        emoji = ":white_check_mark:" if res.valid else ":cross_mark:"
        time_str = (
            f"{time_taken * 1000:.3f} ms" if time_taken < 1.0 else f"{time_taken:.3f} s"
        )

        if show_error_only and res.valid:
            child.visible = False
        else:
            child.update(
                Panel(
                    out_str,
                    title=f"{emoji}  {title}",
                    subtitle=f"Time taken: {time_str}",
                    subtitle_align="right",
                )
            )

    def post_validation_normal(
        self, res: Result, data: _FuncModel, time_taken: float, show_error_only: bool
    ) -> None:
        """
        Prints the result of a validation in a formatted panel.

        Args:
            res (Result): The validation result.
            data (_FuncModel): The function model containing input, expected output, and name.
            time_taken (float): The time taken for the validation.
            show_error_only (bool): Flag indicating whether to show only the error panel.
        """
        input_str = f"{Printer.bold("Input")} - {data.inputs}"
        exp_out_str = f"{Printer.bold("Expected output")} - {data.output}"
        act_out_str = f"{Printer.bold("Actual output")} - {res.data}"

        out_str = f"{input_str}\n{exp_out_str}\n{act_out_str}"

        if res.stdout is not None and res.stdout.strip() != "":
            out_str += f"\n\n{Printer.bold("Stdout")} -\n{res.stdout.strip()}"

        emoji = ":white_check_mark:" if res.valid else ":cross_mark:"
        time_str = (
            f"{time_taken * 1000:.3f} ms" if time_taken < 1.0 else f"{time_taken:.3f} s"
        )
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

    def clean_up(self) -> None:
        """
        Cleans up the printer by clearing the console and stopping the live updates.
        """
        self._console.clear(True)
        self._live.stop()

        print(self._layout)

    def finish(self, total: int, failures: int) -> None:
        """
        Prints the final test execution summary.

        Args:
            total (int): The total number of tests executed.
            failures (int): The number of tests that failed.
        """
        success = Printer.success(f"{total - failures} passed")
        failure = Printer.error(f"{failures} failed")

        status = (
            Printer.success("SUCCESS") if failures == 0 else Printer.error("FAILURE")
        )
        self._console.print(f"{status} | {success} | {failure}")

    def traceback(self):
        """
        Prints the traceback of an exception, including local variables.
        """
        self._console.print_exception(show_locals=True)

    @staticmethod
    def bold(data: str) -> str:
        """
        Formats the given data in bold font weight.

        Args:
            data (str): The data to be formatted.

        Returns:
            str: The formatted message.
        """
        return f"[bold]{data}[/bold]"

    @staticmethod
    def success(data: str) -> str:
        """
        Formats the given data as a success message.

        Args:
            data (str): The data to be formatted.

        Returns:
            str: The formatted success message.
        """
        return f"[bold green]{data}[/bold green]"

    @staticmethod
    def error(data: str) -> str:
        """
        Formats the given data as an error message.

        Args:
            data (str): The error message to format.

        Returns:
            str: The formatted error message.
        """
        return f"[bold red]{data}[/bold red]"

    @staticmethod
    def number(data: int) -> str:
        """
        Formats the given integer as a string with bold blue color.

        Args:
            data (int): The integer to be formatted.

        Returns:
            str: The formatted string.

        """
        return f"[bold blue]{data}[/bold blue]"
