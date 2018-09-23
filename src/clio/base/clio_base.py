# TODO: Add sqlite connector which can write data, and can search for terms in data
# TODO: sqlite stores a) index vocab mapping b) raw docs b) preprocessed docs in terms of mapping c) inverse index of preprocessed doc (in terms of mapping) d) synonym number mapping


from abc import ABC
from abc import abstractclassmethod
import logging
from nesta.packages.nlp_utils import preprocess
from .connectors import SqliteConnector


class NoDocsProvided(Exception):
    '''Exception if no documents have been provided, even though they were expected.'''
    pass


class ClioBase(ABC):

    def __init__(self, db_connector=None, read_only=True, docs=None,
                 ngram_size=3, overwrite_data=False):
        '''Instantiate the Clio object

        Args:
            db_connector (:obj:`connectors.Connector`): Data base connector object (see `connectors`).
            read_only (bool): If `True`, `docs` will be processed for Clio querying and stored in the
                              database via the `db_connector`. If `False`, it is assumed that documents
                              are already available via the `db_connector`.
            docs (:obj:`list` of `str`): List of documents (can be `None` is in `read_only` mode).
            ngram_size (int): The size of n-grams to generaet if not in `read_only` mode.
            overwrite_data (bool): If in `read_only` mode, this flag indicates whether the user would
                                   really like to overwrite any data in the database.
        '''
        # Sanity check of input arguments
        if not read_only and docs is None:
            raise NoDocsProvided("No documents have been provided for training, even though `read_only` is False")
        elif read_only and docs is not None:
            logging.warning("Documents will not be used to the since we are in read_only mode")
        # Default connector is the SqliteConnector
        if db_connector is None:
            db_connector = SqliteConnector()
        db_connector.read_only = read_only
        # Preprocess any documents
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
