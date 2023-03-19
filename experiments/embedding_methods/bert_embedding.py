import json
from pathlib import Path

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
        # add special tokens at the beginning and end of each sentence
        sentence = ["[CLS]" + sentence + "[SEP]"]
        tokenized_texts = self.tokenizer.tokenize(sentence)
        # use the BERT tokenizer to convert tokens to their index numbers
        input_ids = [self.tokenizer.convert_tokens_to_ids(x) for x in tokenized_texts]
        # take the average of the input ID's for each sentence
        output = np.Average(input_ids)

        return output

    def return_hyper_params(self):
        hyper_params = {"Model name": self.model_name,
                        "Padding Strategies": self.tokenizer._get_padding_truncation_strategies()}
        return hyper_params
