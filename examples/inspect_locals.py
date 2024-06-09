# This has not been implemented in the library yet, for testing purposes only
#
# It will either be implemented as a decorator composable with @test
# For example -
# @test(...)
# @inspect_locals
# def foo(...):
#     ...
#
# or as a part of @test
# For example -
# @test(..., inspect_locals=True)
# def foo(...):
#   ...


import sys
import types


# https://stackoverflow.com/a/52358426
def call_function_get_frame(func, *args, **kwargs):
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
    return frame, result


def inspect_locals(func):
    frame, result = call_function_get_frame(func)
    print(f"Local variables: {frame.f_locals}")
    print(f"Result: {result}")

    return func


@inspect_locals
def hello():
    a = 5

    for _ in range(5):
        a += 1
    print("Hello, World!")

    return 5
