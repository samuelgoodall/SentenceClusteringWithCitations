import json
from pathlib import Path

import numpy as np
from experiments.embedding_methods.embedding_interface import EmbeddingInterface
from transformers import BertTokenizer, BertModel
import torch


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
        # tokenize sentences
        encoding = self.tokenizer.encode_plus(sentence, add_special_tokens=True,
                                         truncation=True, padding="max_length",
                                         return_attention_mask=True, return_tensors="pt")
        attention_mask = encoding["attention_mask"][0]
        output = self.model(**encoding)

        # Mean Pooling - Take attention mask into account for correct averaging
        token_embeddings = output[0]  # First element of model_output contains all token embeddings
        input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
        sum_embeddings = torch.sum(token_embeddings * input_mask_expanded, 1)
        sum_mask = torch.clamp(input_mask_expanded.sum(1), min=1e-9)

        return sum_embeddings / sum_mask

    def return_hyper_params(self):
        hyper_params = {"Model name": self.model_name,
                        "Padding Strategies": self.tokenizer._get_padding_truncation_strategies(),
                        "Tokenizer": self.tokenizer}
        return hyper_params
