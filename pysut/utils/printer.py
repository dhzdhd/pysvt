from rich import print
from rich.console import Console
from rich.status import Status
from rich.layout import Layout
from rich.panel import Panel
from typing import Any
from .models import _FuncModel

layout = Layout(name="Tasks")


class Printer:
    def __init__(self, console: Console) -> None:
        self._console = console

    def init(self) -> Status:
        p = Panel("helllo")
        layout.update(p)
        print(layout)

        return self._console.status("Running tests...")
        # add layout, panel, render group

    def pre_validation(self, data: _FuncModel) -> None:
        self._console.print(f"Input - {data.inputs}")
        self._console.print(f"Expected output - {data.output}")

    def post_validation(self, data: Any) -> None:
        self._console.print(f"Actual output - {data}")

    def finish(self, total: int, failures: int) -> None:
        success = Printer.success(f"{total - failures} passed")
        failure = Printer.error(f"{failures} failed")

        status = (
            Printer.success("SUCCESS") if failures == 0 else Printer.error("FAILURE")
        )
        self._console.print(f"{status} | {success} | {failure}")

    def traceback(self):
        self._console.print_exception(show_locals=True)

    @staticmethod
    def success(data: str) -> str:
        return f"[bold green]{data}[/bold green]"

    @staticmethod
    def error(data: str) -> str:
        return f"[bold red]{data}[/bold red]"

    @staticmethod
    def number(data: int) -> str:
        return f"[bold blue]{data}[/bold blue]"
