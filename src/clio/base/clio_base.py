# TODO: Add sqlite connector which can write data, and can search for terms in data
# TODO: sqlite stores a) index vocab mapping b) raw docs b) preprocessed docs in terms of mapping c) inverse index of preprocessed doc (in terms of mapping) d) synonym number mapping


from abc import ABC
from abc import abstractclassmethod
import logging
from nesta.packages.nlp_utils import preprocess
from .connectors import SqliteConnector


class NoDocsProvided(Exception):
    pass


class ClioBase(ABC):

    def __init__(self, db_connector=None, read_only=True, docs=None, ngram_size=3, overwrite_data=False):
        if not read_only and docs is None:
            raise NoDocsProvided
        elif read_only and docs is not None:
            logging.warning("Documents will not be used to the since we are in read_only mode")

        if db_connector is None:
            db_connector = SqliteConnector()
        db_connector.read_only = read_only

        if docs is not None:
            _documents = [preprocess.tokenize_document(doc) for doc in docs]
            _documents = preprocess.build_ngrams(_documents, n=ngram_size)
            db_connector.write(_documents, overwrite_data)
            db_connector.read_only = True

        self.db_connector = db_connector

    @abstractclassmethod
    def train(self):
        pass

    @abstractclassmethod
    def search(self):
        pass

