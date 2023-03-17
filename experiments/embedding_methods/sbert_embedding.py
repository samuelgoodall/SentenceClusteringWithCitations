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
        converts a sentence into SBERT embeddings using the Sentence Transformers package
        ----------
        sentence : str
            the string that is to be embedded
        """
        # Sentences are encoded by calling model.encode()
        embedding = self.model.encode(sentence)
        return embedding
    def return_hyper_params(self):
        hyper_params = {"embedding_dimension": self.model.get_sentence_embedding_dimension(),
                        "model_name": self.model_name,
                        "sentence_features": self.model.get_sentence_features(),
                        "parameters": self.model.get_parameter()}
        return hyper_params
