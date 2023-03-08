import json
from pathlib import Path

import numpy
import numpy as np
from experiments.embedding_methods.embedding_interface import EmbeddingInterface
from sentence_transformers import SentenceTransformer


class SBertEmbedding(EmbeddingInterface):

    def __init__(self, embedding_dimension, sbert_embeddings_path):
        self.embedding_dimension = embedding_dimension
        self.sbert_embeddings_path = sbert_embeddings_path

    def embed_sentence(self, sentence: str):
        """
        converts a sentence into glove embeddings
        if words are not part of the dictionary they are mapped to the zero vector
        ----------
        sentence : str
            the string that is to be embedded
        """
        model = SentenceTransformer('all-MiniLM-L6-v2')
        # Sentences are encoded by calling model.encode()
        embeddings = model.encode(sentence)
        return embeddings
    def return_hyper_params(self):
        hyper_params = {"embedding_dimension": self.embedding_dimension}
        return hyper_params
