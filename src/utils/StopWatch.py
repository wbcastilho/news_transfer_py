import time


class StopWatch:
    def __init__(self):
        self._start_time = time.time()
        self._end_time = time.time()

    @staticmethod
    def _time_convert(sec: float) -> float:
        mins = sec // 60
        sec = sec % 60
        hours = mins // 60
        return mins % 60

    def check(self, timeout: float) -> bool:
        self._end_time = time.time()
        time_elapsed = self._end_time - self._start_time
        min_elapsed = self._time_convert(time_elapsed)

        if min_elapsed < timeout:
            return True
        return False




