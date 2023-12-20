from rich import logging
from rich.console import Console
from rich.status import Status


class Printer:
    def __init__(self, console: Console) -> None:
        self._console = console

    def start(self) -> Status:
        return self._console.status("Running tests...")

    def traceback(self):
        self._console.print_exception(show_locals=True)

    @staticmethod
    def success(data: str) -> str:
        return f"[bold green]{data}[/bold green]"

    @staticmethod
    def error(data: str) -> str:
        return f"[bold red]{data}[/bold red]"

    @staticmethod
    def number(data: str) -> str:
        return f"[bold blue]{data}[/bold blue]"
