import json
from pathlib import Path

import numpy
import numpy as np
from experiments.embedding_methods.embedding_interface import EmbeddingInterface
from sentence_transformers import SentenceTransformer


class SentenceTransformerEmbedding(EmbeddingInterface):

    def __init__(self, model_name: str):
        self.model = SentenceTransformer(model_name)
        self.model_name = model_name

    def embed_sentence(self, sentence: str):
        """
        converts a sentence into glove embeddings
        if words are not part of the dictionary they are mapped to the zero vector
        ----------
        sentence : str
            the string that is to be embedded
        """
        # Sentences are encoded by calling model.encode()
        embedding = self.model.encode(sentence)
        return embedding
    def return_hyper_params(self):
        hyper_params = {"embedding_dimension": self.model.get_sentence_embedding_dimension(),
                        "model_name": self.model_name}
        return hyper_params
