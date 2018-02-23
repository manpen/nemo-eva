from abc import ABC, abstractmethod
from csv import DictWriter
from multiprocessing import Lock
import os


class AbstractStage(ABC):
    """Abstract base class for stages of the data pipeline"""
    @property
    @abstractmethod
    def _stage(self):
        pass

    @property
    def _stagepath(self):
        return (
            os.path.dirname(os.path.realpath(__file__)) +
            "/../data/{}/".format(self._stage)
        )

    def __init__(self):
        self._dict_writer_lock = Lock()
        self._dict_writer = None
        self._results_file = None

    def _save_as_csv(self, a_dict):
        with self._dict_writer_lock:
            if self._dict_writer is None:
                fieldnames = sorted(a_dict.keys())
                if not os.path.exists(self._stagepath):
                    try:
                        os.makedirs(self._stagepath)
                    except FileExistsError:
                        pass
                self._results_file = open(self._stagepath + "results.csv", "w")
                self._dict_writer = DictWriter(self._results_file, fieldnames)
                self._dict_writer.writeheader()
            self._dict_writer.writerow(a_dict)

    @abstractmethod
    def _execute(self):
        pass

    def _close(self):
        if self._results_file is not None:
            self._results_file.close()

    def execute(self):
        self._execute()
        self._close()
