from abc import ABC
from abc import abstractclassmethod


class OverwritePermissionError(Exception):
    pass


class Connector(ABC):
    read_only = False
    conn = None

    @abstractclassmethod
    def __init__(self, *args, **kwargs):
        pass

    def write(self, docs, processed_docs, synonyms, overwrite_data=False):
        if not overwrite_data:
            raise OverwritePermissionError("Attempting to overwrite data, but `overwrite_data` is set to False")
        return self._write(docs, processed_docs, synonyms)

    @abstractclassmethod
    def _write(self, docs, processed_docs, synonyms):
        pass
