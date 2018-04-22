from abc import ABC, abstractmethod
from csv import DictWriter
import multiprocessing
import os

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
        self._dict_queue = multiprocessing.Manager().Queue()

    def _save_as_csv(self, a_dict):
        self._dict_queue.put(a_dict)

    @abstractmethod
    def _execute(self):
        pass

    def execute(self):
        self._execute()
        if not os.path.exists(self._stagepath):
            os.makedirs(self._stagepath)
        first_line = True
        result_dicts = []
        all_keys = set()
        while not self._dict_queue.empty():
            result_dict = self._dict_queue.get()
            result_dicts.append(result_dict)
            all_keys |= set(result_dict.keys())
        with open(self.resultspath, "w") as results_file:
            fieldnames = sorted(all_keys)
            dict_writer = DictWriter(results_file, fieldnames)
            dict_writer.writeheader()
            for result_dict in result_dicts:
                dict_writer.writerow(result_dict)
