from joblib import Parallel, delayed
from tqdm.auto import tqdm
from more_itertools import chunked
import math
from loguru import logger 

def int_ceil(x):
    return int(math.ceil(x))

class ProgressParallel(Parallel):

    def __init__(self, use_tqdm=True, total=None, *args, **kwargs):
        self._use_tqdm = use_tqdm
        self._total = total
        super().__init__(*args, **kwargs)

    def __call__(self, *args, **kwargs):
        with tqdm(disable=not self._use_tqdm, total=self._total) as self._pbar:
            return Parallel.__call__(self, *args, **kwargs)

    def print_progress(self):
        if self._total is None:
            self._pbar.total = self.n_dispatched_tasks
        self._pbar.n = self.n_completed_tasks
        self._pbar.refresh()

def batch_parallel(func1, jobs, batch_size, show_total, *args, **kwargs):
    if show_total:
        jobs = list(jobs)
        total = int_ceil(len(jobs)/batch_size)
    else:
        total = None
    def func(batch):
        res = []
        for job in batch:
            res = func1(job)
        return res
    
    return ProgressParallel(total=total, *args, **kwargs)(delayed(func)(batch) for batch in chunked(jobs, batch_size))

def batch_parallel2(func1, jobs, batch_size, auto_total, kwargs=None):
    kwargs = kwargs or {}
    if auto_total:
        jobs = list(jobs)
        kwargs['total'] = int_ceil(len(jobs)/batch_size)
    def func(batch):
        res = []
        for job in batch:
            res.append(func1(job))
        return res
    logger.info("start processing")
    return ProgressParallel(**kwargs)(delayed(func)(batch) for batch in chunked(jobs, batch_size))


