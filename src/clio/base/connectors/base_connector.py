from abc import ABC
from abc import abstractclassmethod


class OverwritePermissionError(Exception):
    pass


class Connector(ABC):
    read_only = False

    @abstractclassmethod
    def __init__(self, *args, **kwargs):
        pass

    def write(self, docs, processed_docs, synonyms, ngrams, terms, overwrite_data=False):
        if (not overwrite_data) or self.read_only:
            raise OverwritePermissionError("Attempting to overwrite data, but ""(`overwrite_data`,"
                                           "`read_only`) are set to ({},{})".format(overwrite_data, self.read_only))
        return self._write(docs, processed_docs, synonyms, ngrams, terms)

    @abstractclassmethod
    def _write(self, docs, processed_docs, synonyms, ngrams, terms):
        pass
