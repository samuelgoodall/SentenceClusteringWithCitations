import json
from pathlib import Path

import numpy as np
from experiments.embedding_methods.embedding_interface import EmbeddingInterface
from transformers import BertTokenizer, BertModel
import torch


class BertTransformerEmbedding(EmbeddingInterface):

    def __init__(self, model_name: str):
        """
                Parameters
                ----------
                model :
                    Calls the specific pre-trained BERT model
                model_name : str
                    The name of the model
                tokenizer :
                    Calls the tokenizer that the BERT model uses to tokenize sentences
                """
        self.model = BertModel.from_pretrained(model_name)
        self.model_name = model_name
        self.tokenizer = BertTokenizer.from_pretrained(model_name)

    def embed_sentence(self, sentence: str):
        """Returns a value for the sentence embedding by taking the pooled values of each token embedding.

                Parameters
                ----------
                sentence : str
                    The string that is to be embedded
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
        """returns hyperparameters for this embedding model
                """
        hyper_params = {"Model name": self.model_name,
                        "Padding Strategies": self.tokenizer._get_padding_truncation_strategies(),
                        "Tokenizer": self.tokenizer}
        return hyper_params
