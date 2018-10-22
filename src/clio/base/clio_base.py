from abc import ABC
from abc import abstractclassmethod
import logging
from .connectors import SqliteConnector
from nesta.packages.nlp_utils import preprocess


class NoDocsProvided(Exception):
    '''Exception if no documents have been provided, even though they were expected.'''
    pass


class NoOverwrite(Exception):
    '''Exception if documents have been provided, even though we are not in overwrite mode.'''
    pass


class ClioBase(ABC):

    def __init__(self, db_connector=None, read_only=True, overwrite_data=False):
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
            lower_tfidf_limit(float): Lower percentile limit for TFIDF cut.
            upper_tfidf_limit(float): Upper percentile limit for TFIDF cut.
        '''
        # Default connector is the SqliteConnector
        if db_connector is None:
            db_connector = SqliteConnector()
        db_connector.read_only = read_only
        self.db_connector = db_connector
        self.overwrite_data = overwrite_data

    @abstractclassmethod
    def train(self, raw_docs):
        pass

    @abstractclassmethod
    def query(self, q):
        pass
