import pytest, time
from parallel_ex import ParallelEx
from functools import partial

def some_function(n):
    for i in range(n):
        time.sleep(0.2)
        yield i

def test_run_n_times():
    fun = partial(some_function, 10)
    ParallelEx.run_n_times(fun, n=5, total=10, n_cpu=2)

def test_run_kwargs():
    totals = [25,8,6,22,12,6,10,9]
    kwargs = [{'n':i} for i in totals]
    ParallelEx.run_kwargs(some_function, kwargs, totals=totals, n_cpu=3)

if __name__ == "__main__":
    test_run_n_times()
    test_run_kwargs()
