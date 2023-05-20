import abc
from enum import Enum

import numpy as np


class SentenceCitationFusingMethod(Enum):
    Concatenation = 1
    Averaging = 2
class EmbeddingInterface(metaclass=abc.ABCMeta):
    @staticmethod
    def fuse_sentence_and_citation_embedding(sentence_embedding, citation_embeddings:list,
                                         sentence_citation_fusing_method: SentenceCitationFusingMethod):
        """
        sentence_citation_fusing_method: SentenceCitationPoolingMethod
            method to be used for fusing sentence and citation concat or average

        Parameters
        ----------
        sentence_embedding :
            a vector representation of the sentence
        sentence_citation_embedding:
            a vector representation of the citation
        sentence_citation_fusing_method:
            the method used for fusing the embeddings can be concatenation or averaging

        Returns
        -------
        numpy array
            numpy array that is the vector representation of both combined
        """
        pooled_citation_embedding = np.array(np.mean(np.mat(citation_embeddings), axis=0, dtype=np.float64))[0]
        fused_embedding = any
        if sentence_citation_fusing_method == SentenceCitationFusingMethod.Averaging:
            fused_embedding =  (sentence_embedding + pooled_citation_embedding) / 2
        if sentence_citation_fusing_method == SentenceCitationFusingMethod.Concatenation:
            fused_embedding = np.concatenate((sentence_embedding, pooled_citation_embedding), axis=0)
        return fused_embedding
    
    @classmethod
    def __subclasshook__(cls, subclass):
        return (((hasattr(subclass, 'embed_sentence') and
                callable(subclass.embed_sentence)) or
                (hasattr(subclass,'embedded_sentences') and
                callable(subclass.embeddedSentences))) and
                hasattr(subclass,'return_hyper_params') and
                callable(subclass.return_hyper_params) or NotImplemented)

    
    @abc.abstractmethod
    def embed_sentences(self, sentences, use_citation):
        """embeds the sentences"""
        raise NotImplementedError
    
    @abc.abstractmethod
    def embed_sentence(self, sentence: str):
        """embeds the sentence"""
        raise NotImplementedError

    @abc.abstractmethod
    def return_hyper_params(self)->dict:
        """returns the hyperparameters used as dict"""
        raise NotImplementedError
    