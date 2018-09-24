import os
import datetime
from clio.base.connectors.sqlite_connector import SqliteConnector
import unittest


docs = {0: 'This is some sample text', 1: 'This is another part of verse'}
processed_docs = {0: ((0, 1),   # sample
                      (1, 1)),  # text
                  1: ((2, 1),   # another
                      (0, 1),   # part_of = sample
                      (1, 1))}  # verse = text

synonyms = {0: ((0, False),    # sample
                (0, True)),    # part_of
            1: ((1, False),    # text
                (2, False)),   # verse
            2: ((3, False),)}  # another

ngrams = {0: ((4, 0),   # part
              (5, 0))}  # of

terms = {0: "sample",
         1: "text",
         2: "verse",
         3: "another",
         4: "part",
         5: "of"}


class SqliteConnectorTest(unittest.TestCase):

    def setUp(self):
        _ts = datetime.datetime.now().timestamp()
        ts = str(_ts).split(".")[0]
        self.db_name = 'test_{}'.format(ts)
        self.conn = SqliteConnector(self.db_name)

    def tearDown(self):
        os.remove('{}.db'.format(self.db_name))

    def test_write(self):
        ''''''
        self.conn.write(docs, processed_docs, synonyms, ngrams, terms, True)


if __name__ == '__main__':
    unittest.main()
