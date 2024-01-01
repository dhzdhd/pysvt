from rich import print
from rich.console import Console
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.status import Status

from .models import Result, _FuncModel


class Printer:
    def __init__(self, console: Console, is_live: bool) -> None:
        self._console = console
        self._is_live = is_live
        self._layout = Layout()

    def init_live(self, data: list[_FuncModel]) -> Live:
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
        return Status("Running tests")

    def pre_validation(self, index: int, data: _FuncModel) -> None:
        child = next(filter(lambda x: x.name == data.name, self._layout.children))

        string = f"Input - {data.inputs}\nExpected output - {data.output}"
        child.update(Panel(string, title=data.name))

    def post_validation(
        self, res: Result, title: str, time_taken: float, show_error_only: bool
    ) -> None:
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
        out_str = f"Input - {data.inputs}\nExpected output - {data.output}\nActual output - {res.data}"
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
        self._console.clear(True)
        self._live.stop()

        print(self._layout)

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
