from clio.base.connectors.base_connector import Connector
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import Float
from sqlalchemy import Text
from sqlalchemy import Boolean
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

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
    term = Column(Text)


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
