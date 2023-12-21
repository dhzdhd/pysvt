from rich import print
from rich.console import Console, ConsoleOptions, Group
from rich.status import Status
from rich.layout import Layout
from rich.panel import Panel
from typing import Any
from .models import _FuncModel, Result
from rich.live import Live, VerticalOverflowMethod


class Printer:
    def __init__(self, console: Console) -> None:
        self._console = console
        self._layout = Layout()

    def init(self, data: list[_FuncModel]) -> Status:
        for index, item in enumerate(data):
            l = Layout(
                Panel(item.name, title=item.name),
                name=index,
            )
            self._layout.add_split(l)

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

    def pre_validation(self, index: int, data: _FuncModel) -> None:
        l = self._layout.children[index]
        string = f"Input - {data.inputs}\nExpected output - {data.output}"
        l.update(Panel(string, title=data.name))

    def post_validation(self, index: int, res: Result, title: str) -> None:
        l = self._layout.children[index]

        string = f"{str(l.renderable.renderable)}\nActual output - {res.data}"
        emoji = ":white_check_mark:" if res.valid else ":cross_mark:"

        l.update(
            Panel(
                string,
                title=f"{emoji}  {title}",
                subtitle="Time taken: 100ms",
                subtitle_align="right",
            )
        )

    def finish(self, total: int, failures: int) -> None:
        self._console.clear(True)
        self._live.stop()

        print(self._layout)

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
