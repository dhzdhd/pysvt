"""Context utility to provide timer context manager."""

import time
from typing import Any, final


@final
class Timer:
    """A context manager for timing a block of code.

    On entry, records the start time and returns a callable that, when
    invoked, returns the elapsed duration in seconds since entry. The
    duration is only finalized once the `with` block exits.
    """

    def __init__(self) -> None:
        """Initialize the timer with start and end times set to zero."""
        self._start = 0.0
        self._end = 0.0

    def __enter__(self):
        """Start the timer and return a callable that reports elapsed time.

        :return: A no-argument callable returning the elapsed time in
            seconds. The value is only accurate after `__exit__` has run.
        """
        self._start = time.perf_counter()
        return lambda: self._end - self._start

    def __exit__(self, *args: list[Any]):
        """Stop the timer, recording the end time.

        :param args: Exception info passed by the context manager protocol
            (type, value, traceback), unused here.
        """
        self._end = time.perf_counter()
