import os
import sys


class PrintBlocker(object):
    '''
    A context manager that blocks output for its scope.
    '''

    def __init__(self, *args, **kw):
        self._orig = [sys.stdout, sys.stderr]
        self._orig_fileno = [os.dup(el.fileno()) for el in self._orig]
        self._devnull = [os.open(os.devnull, os.O_WRONLY) for el in self._orig]

    def __enter__(self):
        for el in self._orig:
            el.flush()
        for i, devnull in enumerate(self._devnull):
            new = os.dup(i+1)
            os.dup2(devnull, i+1)
            os.close(devnull)

    def __exit__(self, exc_type, exc_val, exc_tb):
        for el in self._orig:
            el.flush()
        sys.stdout, sys.stderr = self._orig
        for i, orig_fileno in enumerate(self._orig_fileno):
            os.dup2(orig_fileno, i+1)
