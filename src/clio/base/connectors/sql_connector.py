from .connectors.base_connector import Connector
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Boolean
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

Base = declarative_base()


class Synonym(Base):
    __tablename__ = 'synonyms'

    synonyn_id = Column(Integer, primary_key=True)
    term = Column(String, primary_key=True)

    def __repr__(self):
        return "%s" % self.synonym_id


class NGram(Base):
    __tablename__ = 'ngrams'
    gram_id = Column(Integer, primary_key=True)
    term = Column(Integer, primary_key=True)
    term_position = Column(Integer, primary_key=True)
    gram = Column(String, null=False)

    def __repr__(self):
        return "%s" % self.gram


class SqliteConnector(Connector):
    inverse_index_table = None

    def __init__(self, database_name="default"):
        self.engine = create_engine('sqlite:///{}.db'.format(database_name))

    def _write(self, docs, processed_docs, synonyms, ngrams):

        # Generate the inverse_index table schema
        attr_dict = {'__tablename__': 'inverse_index',
                     'id': Column(Integer, primary_key=True)}
        for syn in set(synonyms):
            attr_dict[set(syn)] = Column(Boolean, default=0)
        self.inverse_index_table = type('InverseIndexTable', (Base,), attr_dict)

        Session = sessionmaker(bind=self.engine)
        session = Session()

        for gram_id, (term, term_position, gram) in ngrams.items():
            ngram = NGram(gram_id=gram_id, term=term, term_position=term_position, gram=gram)
            session.add(ngram)

        for syn, term in synonyms.items():
            synonym = Synonym(synonyn_id=syn, term=term)
            session.add(synonym)

        for idoc, _doc in enumerate(processed_docs):
            idx = self.inverse_index_table(id=idoc, **{str(term): True for term in _doc})
            session.add(idx)

        session.commit()
        session.close()

    
