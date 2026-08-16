"""Validation utility to capture local variable information."""

import linecache
import sys
from types import FrameType
from typing import Any, Callable, Literal

from pysvt.utils.models import Variable


def get_result_locals(
    func: Callable[..., Any], *args: list[Any], **kwargs: dict[str, Any]
) -> tuple[Any, list[Variable]]:
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
    target_frame: FrameType | None = None
    snapshots: list[Variable] = []
    old_trace = sys.gettrace()

    def tracer(frame: FrameType, event: Literal["call", "line", "return", "exception", "opcode"], _arg: Any):
        """Trace function that captures the frame on the first 'call' event.

        :param frame: The frame being traced.
        :param event: The type of trace event.
        :param _arg: Event-specific argument (unused).
        :return: The original trace function, to keep tracing enabled.
        """
        nonlocal target_frame
        if event == "call" and target_frame is None:
            target_frame = frame
            return tracer
        if event == "line" and frame is target_frame:
            code = linecache.getline(frame.f_code.co_filename, frame.f_lineno).strip()
            snapshots.append(
                Variable(list(frame.f_locals.keys()), list(frame.f_locals.values()), frame.f_lineno, code)
            )
        return tracer

    sys.settrace(tracer)
    try:
        result = func(*args, **kwargs)
    finally:
        sys.settrace(old_trace)

    return (result, snapshots)
