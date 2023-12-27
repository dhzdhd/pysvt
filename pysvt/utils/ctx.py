import time


class Timer:
    def __init__(self) -> None:
        self._start = 0.0
        self._end = 0.0

    def __enter__(self):
        self._start = time.perf_counter()
        return lambda: self._end - self._start

    def __exit__(self, *args):
        self._end = time.perf_counter()
