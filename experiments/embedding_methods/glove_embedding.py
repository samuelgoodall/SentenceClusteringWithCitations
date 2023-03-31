from pathlib import Path

import numpy
import numpy as np
import spacy
from gensim.models import KeyedVectors

from experiments.embedding_methods.embedding_interface import EmbeddingInterface


class GloveEmbedding(EmbeddingInterface):

    def __init__(self, embedding_dimension, glove_embeddings_path):
        self.embedding_dimension = embedding_dimension
        self.glove_embeddings = self._get_glove_embeddings_keyed_vectors(glove_embeddings_path)
        self.glove_embeddings_path = glove_embeddings_path

    def _get_glove_embeddings_keyed_vectors(self, glove_embeddings_path):
        """
        gets the glove_embeddings as gensim KeyedVectors

        Parameters
        ----------
        glove_embeddings_path : str
            path to the glove embeddings saved as txt
        Returns
        -------
        keyed vectors
            keyed vectors in essence just a big dictionary with the words as keys
        """
        word2vec_glove_file = glove_embeddings_path.split('.txt')[0] + "word2vec" + ".kv"
        if Path(word2vec_glove_file).is_file():
            return KeyedVectors.load(word2vec_glove_file)
        else:
            keyed_vecs = KeyedVectors.load_word2vec_format(glove_embeddings_path, binary=False, no_header=True)
            keyed_vecs.save(word2vec_glove_file)
            return keyed_vecs

    def embed_sentence(self, sentence: str):
        """
        converts a sentence into glove embeddings
        if words are not part of the dictionary they are mapped to the zero vector

        Parameters
        ----------
        sentence : str
            the string that is to be embedded

        Returns
        -------
        numpy array
            the embedding vector
        """
        words = sentence.lower().split()
        count = 0
        sentence_embedding = np.zeros(self.embedding_dimension)
        word_embeddings = []
        for word in words:
            try:
                word_embeddings.append(self.glove_embeddings[word])
                count += 1
            except KeyError:
                continue
            except FloatingPointError:
                print("Floating Point ERROR!")

        if count != 0:
            return np.mean(np.array(word_embeddings), axis=0, dtype=np.float64)
        else:
            return sentence_embedding

    def return_hyper_params(self):
        """
        returns the hyper params as dict it is dict in order to keep it flexible

        Returns
        -------
        dict
            the hyper_params as a dictionary
        """
        hyper_params = {"embedding_dimension": self.embedding_dimension,
                        "glove_embeddings_path": self.glove_embeddings_path}
        return hyper_params
