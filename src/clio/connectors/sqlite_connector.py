from clio.base.connectors.base_connector import Connector
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import Float
from sqlalchemy import Text
from sqlalchemy import String
from sqlalchemy import Boolean
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from operator import itemgetter
from collections import defaultdict
from collections import Counter

##
# TODO: MOVE TO NLP_UTILS
##
def knuth_morris_pratt(text, pattern, overlaps=False):
    '''Yields all starting positions of copies of the pattern in the text.
Calling conventions are similar to string.find, but its arguments can be
lists or iterators, not just strings, it returns all matches, not just
the first one, and it does not need the whole text in memory at once.
Whenever it yields, it will have read the text exactly up to and including
the match that caused the yield.'''

    # allow indexing into pattern and protect against change during yield
    pattern = list(pattern)

    # build table of shift amounts
    shifts = [1] * (len(pattern) + 1)
    shift = 1
    for pos in range(len(pattern)):
        while shift <= pos and pattern[pos] != pattern[pos-shift]:
            shift += shifts[pos-shift]
        shifts[pos+1] = shift

    # do the actual search
    startPos = 0
    matchLen = 0
    lastMatch = -len(pattern)
    for c in text:
        while matchLen == len(pattern) or \
              matchLen >= 0 and pattern[matchLen] != c:
            startPos += shifts[matchLen]
            matchLen -= shifts[matchLen]
        matchLen += 1
        if matchLen == len(pattern):
            if overlaps or startPos >= lastMatch + len(pattern):
                yield startPos
                lastMatch = startPos


Base = declarative_base()


class InverseIndex(Base):
    __tablename__ = 'inverse_index'

    doc_id = Column(Integer, primary_key=True, index=True)
    synonym_id = Column(Integer, primary_key=True, index=True)
    weight = Column(Float, default=0)


class Synonym(Base):
    __tablename__ = 'synonyms'

    synonym_id = Column(Integer, primary_key=True, index=True)
    term_id = Column(Integer, primary_key=True, index=True)
    is_ngram = Column(Boolean, primary_key=True)


class NGram(Base):
    __tablename__ = 'ngrams'

    ngram_id = Column(Integer, primary_key=True, index=True)
    term_id = Column(Integer, primary_key=True)
    term_position = Column(Integer, primary_key=True)


class Term(Base):
    __tablename__ = 'terms'

    term_id = Column(Integer, primary_key=True)
    term = Column(String, index=True)


class RawDoc(Base):
    __tablename__ = 'raw_docs'

    doc_id = Column(Integer, primary_key=True)
    doc = Column(Text)


class SqliteConnector(Connector):
    inverse_index_table = None

    def __init__(self, database_name="default"):
        self.engine = create_engine('sqlite+pysqlite:///{}.db'.format(database_name))
        self.engine.connect()
        Base.metadata.create_all(self.engine)

    def _write(self, docs, processed_docs, synonyms, ngrams, terms):

        #
        inputs = []
        inputs += [RawDoc(doc_id=doc_id, doc=str(doc)) for doc_id, doc in docs.items()]
        inputs += [InverseIndex(doc_id=doc_id, synonym_id=synonym_id, weight=weight)
                   for doc_id, info in processed_docs.items()
                   for synonym_id, weight in info]
        inputs += [Synonym(synonym_id=synonym_id, term_id=term_id, is_ngram=is_ngram)
                   for synonym_id, info in synonyms.items()
                   for term_id, is_ngram in info]
        inputs += [NGram(ngram_id=ngram_id, term_id=term_id, term_position=term_position)
                   for ngram_id, info in ngrams.items()
                   for term_id, term_position in info]
        inputs += [Term(term_id=term_id, term=term) for term_id, term in terms.items()]

        # Done
        Session = sessionmaker(bind=self.engine)
        session = Session()
        session.add_all(inputs)
        session.commit()
        session.close()

    def find_docs_by_term(self, term_id, is_ngram):
        Session = sessionmaker(bind=self.engine)
        session = Session()
        condition = (Synonym.term_id == term_id) & (Synonym.is_ngram == is_ngram)
        synonyms = [s[0] for s in session.query(Synonym.synonym_id).filter(condition).all()]
        results = defaultdict(float)
        for s in synonyms:
            for iidx in session.query(InverseIndex).filter(InverseIndex.synonym_id == s).all():
                results[iidx.doc_id] += iidx.weight
        session.close()
        return Counter(results)

    def terms_to_ids(self, terms):
        '''Look up terms'''
        Session = sessionmaker(bind=self.engine)
        session = Session()
        raw_term_ids = [session.query(Term.term_id).filter(Term.term == term).one()[0]
                        for term in terms]
        session.close()
        return raw_term_ids

    def find_and_replace_ngrams(self, raw_term_ids):
        '''Check whether the query term is an ngram'''
        Session = sessionmaker(bind=self.engine)
        session = Session()
        raw_term_set = set(raw_term_ids)

        # Find possible ngrams
        ngrams = {}
        for ngram_id, in session.query(NGram.ngram_id).group_by(NGram.ngram_id).all():
            # Build the ngram as a mapping of position: term
            # BUT set the position to False if the term isn't
            # in `raw_term_ids`
            query = session.query(NGram).filter(NGram.ngram_id == ngram_id)
            ngram = [_ngram.term_id
                     if _ngram.term_id in raw_term_set else None
                     for _ngram in query.order_by(NGram.term_position).all()]
            if None in ngram:
                continue
            ngrams[ngram_id] = ngram
        session.close()

        # Find the position of these ngrams, starting with large ngrams
        for ngram_id, ngram in sorted(ngrams.items(),
                                      key=lambda x: len(itemgetter(1)(x)),
                                      reverse=True):
            # Replace occurences of the ngram, starting with the final position
            # (easier to remove from the end than recalculate the index, so
            # using `reversed`)
            ngram_positions = list(knuth_morris_pratt(raw_term_ids, ngram))
            for pos in reversed(ngram_positions):
                del raw_term_ids[pos+1: pos+len(ngram)]
                raw_term_ids[pos] = ngram_id

        term_ids = [{"term_id": id_, "is_ngram": (id_ < 0)}
                    for id_ in raw_term_ids]
        return term_ids
