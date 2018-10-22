from .base.clio_base import ClioBase
from pcst import PrincipalComponentSegmentationTree as PCST
from gensim.models import Word2Vec
from nesta.packages.nlp_utils import preprocess
from sklearn.feature_extraction.text import CountVectorizer
import numpy as np


class KeywordSearch(ClioBase):

    def process_docs(self, raw_docs, ngram_size=3,
                     lower_tfidf_limit=0.35, upper_tfidf_limit=0.95):
        rawish_docs = [preprocess.tokenize_document(doc) for doc in raw_docs]
        rawish_docs, raw_ngrams = preprocess.build_ngrams(rawish_docs, n=ngram_size,
                                                          return_ngrams=True)
        rawish_docs = preprocess.filter_by_tfidf(rawish_docs, lower_tfidf_limit, upper_tfidf_limit)
        return rawish_docs, raw_ngrams

    def process_terms(self, rawish_docs, rawish_synonyms, ngram_char="_"):
        cv = CountVectorizer(binary=True)
        cv.fit(rawish_docs)

        # Process terms
        inverse_terms, terms = {}, {}
        for idx, feature in enumerate(cv.get_feature_names()):
            idx = idx+1  # To avoid idx == 0 (which causes problems for ngram indexing)
            inverse_terms[feature] = idx
            if ngram_char in feature:
                idx = -idx
            terms[idx] = feature

        # Process ngrams
        ngrams = {}
        for idx, feature in terms.items():
            if idx > 0:
                continue
            _terms = []
            for feature_pos, _feature in enumerate(feature.split(ngram_char)):
                term_idx = inverse_terms[_feature]
                _terms.append((term_idx, feature_pos))
            ngrams[-idx] = tuple(_terms)

        # Process docs
        docs = {}
        for idoc, bow in enumerate(cv.transform(rawish_docs)):
            doc = []
            for idx, exists in enumerate(bow):
                if not exists:
                    continue
                idx = idx+1  # To avoid idx == 0 (which causes problems for ngram indexing)
                if idx in terms:
                    row = (idx, 1)
                else:
                    row = (-idx, 1)
                doc.append(row)
            docs[idoc] = tuple(doc)

        # Process synonyms
        synonyms = {}
        for isyn, words in enumerate(rawish_synonyms):
            synonyms[isyn] = tuple(inverse_terms[w] for w in words)

        # Done
        return docs, terms, ngrams, synonyms

    @staticmethod
    def train_bare_wv(*w2v_args, **w2v_kwargs):
        model = Word2Vec(*w2v_args, **w2v_kwargs)
        model.wv.init_sims(replace=True)
        vectors = model.wv.vectors
        words = np.array(model.wv.index2word)
        del model
        return vectors, words

    def train(self, raw_docs):
        rawish_docs = self.process_docs(raw_docs)
        vectors, words = self.train_bare_wv(rawish_docs, size=300,
                                            window=5, min_count=1, workers=4)
        pcst = PCST(data=vectors, min_leaf_size=500, num_cores=2)
        rawish_synonyms = pcst.generate_clusters(words)
        docs, terms, ngrams, synonyms = self.process_terms(rawish_docs, rawish_synonyms)
        self.db_connector.write_raw_docs(raw_docs)
        self.db_connector.write_docs(docs)
        self.db_connector.write_terms(terms)
        self.db_connector.write_ngrams(ngrams)
        self.db_connector.write_synonyms(synonyms)
