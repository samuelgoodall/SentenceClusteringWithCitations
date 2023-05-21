import itertools
import pickle
from os import path

import numpy as np
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer

from experiments.embedding_methods.embedding_interface import (
    EmbeddingInterface, SentenceCitationFusingMethod)


class TfIdfEmbedding(EmbeddingInterface):
    path = "./embedding_methods/embeddings/"
    def __init__(self):
        self.hyper_parameter = {
            'stop_words': 'english',
            'lowercase': True, 
            'max_features': 10000,
            'strip_accents':'ascii'
        }
        self.content_vectorizer = TfidfVectorizer(**self.hyper_parameter)
        self.citation_vectorizer = TfidfVectorizer(**self.hyper_parameter)
        self.epsilon = 0.001
        
    def embed_sentences(self, sentences, use_citation):
        if use_citation:
            return self.embed_sentences_with_citations(sentences)
        else:
            return self.embed_sentences_without_citations(sentences)
    
    def embed_sentences_with_citations(self, sentences):
        contents = [sentence.sentence for sentence in sentences]
        all_citations = [sentence.citations for sentence in sentences]
        citations_titles = []
        citations_titles_length = []
        for citations in all_citations:
            citations_titles_length.append(len(citations))
            citations_titles.append([citation.citation_title for citation in citations])
        flatted_citation_titles = list(itertools.chain.from_iterable(citations_titles))
        citations_embeddings_flatted = self.citation_vectorizer.transform(flatted_citation_titles)
        citations_embeddings = []
        current_pos = 0
        for length in citations_titles_length:
            citations_embeddings.append(citations_embeddings_flatted[current_pos:current_pos+length])
            current_pos += length
        contents_embeddings = self.content_vectorizer.transform(contents)
        embeddings = []
        for i in range(len(contents)):
            prepared_content_embedding = contents_embeddings[i].toarray()[0]
            prepared_citations_embeddings = citations_embeddings[i].toarray()
            embeddings.append(self.fuse_sentence_and_citation_embedding(prepared_content_embedding, prepared_citations_embeddings, SentenceCitationFusingMethod.Concatenation).tolist()+self.epsilon*np.ones(len(self.fuse_sentence_and_citation_embedding(prepared_content_embedding, prepared_citations_embeddings, SentenceCitationFusingMethod.Concatenation).tolist())))
        return embeddings
    
    def embed_sentences_without_citations(self, sentences):
        sentences = [sentence.sentence for sentence in sentences]
        embeddings = self.content_vectorizer.transform(sentences)
        cluster_compatible_embeddings = embeddings.toarray().tolist()
        for i,embedding in enumerate(cluster_compatible_embeddings):
            cluster_compatible_embeddings[i] += self.epsilon*np.ones(len(cluster_compatible_embeddings[i]))
        return cluster_compatible_embeddings
    
    def return_hyper_params(self):
        return self.hyper_parameter
    
    def embed_sentence(self, sentence):
        return ""
    
    def load(self):
        files_exist = path.exists(self.path + "tf_idf_content.pkl") and path.exists(self.path + "tf_idf_citation.pkl")
        if not files_exist:
            raise Exception("No tf_idf files found")
        self.content_vectorizer = pickle.load(open(self.path + "tf_idf_content.pkl", "rb"))
        self.citation_vectorizer = pickle.load(open(self.path + "tf_idf_citation.pkl", "rb"))
    
    def setup(self, all_sentences):
        content = [sentence.sentence for sentence in all_sentences]
        citations = [sentence.citations for sentence in all_sentences]
        citations = list(itertools.chain.from_iterable(citations))
        citation_titles = [citation.citation_title for citation in citations]
        self.content_vectorizer.fit(content)
        self.citation_vectorizer.fit(citation_titles)
        pickle.dump(self.content_vectorizer, open(self.path + "tf_idf_content.pkl", "wb"))
        pickle.dump(self.citation_vectorizer, open(self.path + "tf_idf_citation.pkl", "wb"))