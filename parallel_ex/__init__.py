import sys, shutil, math, multiprocessing
from functools import partial
from itertools import repeat
from typing import Any, Callable, Collection, Optional, Union
from dataclasses import dataclass
from multiprocessing import Manager, Process, Pool, Queue

def wrap_function(func:Callable, queue:Queue)->None:
    for i in func(): queue.put(i)

@dataclass
class Bar:
    total:int
    n:int=0
    symbol:str='='
    idx:Optional[int]=None

    def step(self, print:bool=False, **kwargs:Any)->None:
        self.n += 1
        if print: self.print(**kwargs)

    def print(self)->None:
        max_width, _ = shutil.get_terminal_size()
        bar_width = max_width - 7
        p = self.n / self.total
        progress = int(round(100*p))
        filled = int(round(bar_width*p))
        blank = bar_width - filled
        msg = f'[{self.symbol*filled}{" "*blank}] {progress:3d}%'
        print(msg)

class ParallelEx:
    def __init__(self, funcs:Collection[Callable], totals:Union[int,Collection[int]], n_cpu:Optional[int]=None):
        if n_cpu is None: n_cpu = multiprocessing.cpu_count()
        if isinstance(totals, int): totals = list(repeat(totals,len(funcs)))
        assert len(funcs)==len(totals)
        self.funcs,self.totals,self.n_cpu = funcs,totals,n_cpu
        self._build_pbars()

    def __len__(self)->int: return len(self.funcs)

    def _build_pbars(self)->None:
        self.main_bar = Bar(len(self), symbol='#')
        self.bars = [Bar(total=total, idx=i) for i,total in enumerate(self.totals)]

    def _run(self)->None:
        with Pool(processes=self.n_cpu) as pool, Manager() as manager:
            queues = [manager.Queue(total) for total in self.totals]
            res = [pool.apply_async(wrap_function, (func,queue)) for func,queue in zip(self.funcs,queues)]
            pool.close()
            self.print()
            i = 0
            while True:
                if i == len(self): break
                for queue,r,bar in zip(queues,res,self.bars):
                    if not queue.empty():
                        try:
                            v = queue.get_nowait()
                            bar.step()
                            self.print(refresh=True)
                        except:
                            pass
                        finally:
                            if r.ready():
                                self.main_bar.step()
                                i += 1

            pool.join()
            self.print(refresh=True)

        return [r.get() for r in res]

    def print(self, refresh:bool=False)->None:
        if refresh:
            for _ in repeat(None, len(self)+2):
                sys.stdout.write('\033[F') #back to previous line
                sys.stdout.write('\033[K') #clear line

        self.main_bar.print()
        print(f'{len(self)} tasks running in {self.n_cpu} processes:')
        for b in self.bars: b.print()

    @classmethod
    def run_kwargs(cls, func:Callable, kwargs:Collection[dict], totals:Union[int,Collection[int]],
                   n_cpu:Optional[int]=None)->list:
        '''Run `func` with different `kwargs`.
        - totals: expected number of elements to get back for each `kwargs`.'''
        funcs = [partial(func, **kw) for kw in kwargs]
        ex = cls(funcs, totals, n_cpu=n_cpu)
        return ex._run()

    @classmethod
    def run_n_times(cls, func:Callable, n:int, total:int, n_cpu:Optional[int]=None)->list:
        '''Run same function `n` times.
        - total: expected number of elements to get back.'''
        funcs = list(repeat(func, n))
        ex = cls(funcs, total, n_cpu=n_cpu)
        return ex._run()
