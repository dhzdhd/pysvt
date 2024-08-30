import sys
import types
from typing import Callable, Any


def get_result_locals(
    func: Callable[..., Any], *args, **kwargs
) -> tuple[Any, dict[str, Any]]:
    frame: types.FrameType | None = None
    trace = sys.gettrace()

    def snatch_locals(_frame, name, arg):
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

    return (result, frame.f_locals)
