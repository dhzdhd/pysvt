"""Validation utility to capture local variable information."""

import sys
from types import FrameType
from typing import Any, Callable, Literal


def get_result_locals(
    func: Callable[..., Any], *args: list[Any], **kwargs: dict[str, Any]
) -> tuple[Any, dict[str, Any] | None]:
    """Call a function and capture its local variables at return time.

    Uses `sys.settrace` to snoop the frame of the first call into `func`,
    then reads its `f_locals` after the function returns.

    :param func: The function to call and inspect.
    :param args: Positional arguments to pass to `func`.
    :param kwargs: Keyword arguments to pass to `func`.
    :return: A tuple of the function's return value and a dict of its
        local variables, or `None` for the locals if the frame was never
        captured.
    """
    frame: FrameType | None = None
    trace = sys.gettrace()

    def snatch_locals(
        _frame: FrameType, name: Literal["call", "line", "return", "exception", "opcode"], _arg: Any
    ):
        """Trace function that captures the frame on the first 'call' event.

        :param _frame: The frame being traced.
        :param name: The type of trace event.
        :param _arg: Event-specific argument (unused).
        :return: The original trace function, to keep tracing enabled.
        """
        nonlocal frame
        if frame is None and name == "call":
            frame = _frame
            sys.settrace(trace)
        return trace

    sys.settrace(snatch_locals)
    try:
        result = func(*args, **kwargs)
    finally:
        sys.settrace(trace)

    locals = frame.f_locals if frame is not None else None

    return (result, locals)
