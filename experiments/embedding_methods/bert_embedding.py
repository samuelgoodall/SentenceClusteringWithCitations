import json
from pathlib import Path

import numpy
import numpy as np
from experiments.embedding_methods.embedding_interface import EmbeddingInterface
from transformers import BertTokenizer, BertModel


class BertTransformerEmbedding(EmbeddingInterface):

    def __init__(self, model_name: str):
        self.model = BertModel.from_pretrained(model_name)
        self.model_name = model_name
        self.tokenizer = BertTokenizer.from_pretrained(model_name)

    def embed_sentence(self, sentence: str):
        """
        sentence : str
            the string that is to be embedded
        """
        encoded_input = self.tokenizer(sentence, return_tensors='pt')
        output = self.model(**encoded_input)

        return output

    def return_hyper_params(self):
        hyper_params = {"embedding_dimension": self.,
                        "model_name":}
        return hyper_params
