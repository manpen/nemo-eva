from abc import ABC, abstractmethod
from csv import DictWriter
import multiprocessing
import os
import threading

from config import data_path


class classproperty(object):
    def __init__(self, f):
        self.f = f

    def __get__(self, obj, owner):
        return self.f(owner)


class AbstractStage(ABC):
    """Abstract base class for stages of the data pipeline"""
    @classproperty
    @abstractmethod
    def _stage(self):
        pass

    @classproperty
    def _stagepath(self):
        return data_path() + self._stage + "/"

    @classproperty
    def resultspath(self):
        return (
            self._stagepath + "results.csv"
        )

    def __init__(self):
        self._results_initialized = False
        self._lock = multiprocessing.Lock()

    def _save_as_csv(self, a_dict):
        with self._lock:
            if not self._results_initialized:
                self._results_initialized = True
                with open(self.resultspath, "w") as results_file:
                    fieldnames = sorted(set(a_dict.keys()))
                    dict_writer = DictWriter(results_file, fieldnames)
                    dict_writer.writeheader()
                    dict_writer.writerow(a_dict)
            else:
                with open(self.resultspath, "a") as results_file:
                    fieldnames = sorted(set(a_dict.keys()))
                    dict_writer = DictWriter(results_file, fieldnames)
                    dict_writer.writerow(a_dict)
                    

    @abstractmethod
    def _execute(self):
        pass

    def execute(self):
        if not os.path.exists(self._stagepath):
            os.makedirs(self._stagepath)
        self._execute()
