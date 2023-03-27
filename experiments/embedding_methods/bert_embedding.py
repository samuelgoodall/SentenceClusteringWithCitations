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
        model_name : str
            The name of the BERT model to be used
        """
        self.device = "cuda:0" if torch.cuda.is_available() else "cpu"
        self.model = BertModel.from_pretrained(model_name).to(self.device)
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
                                         return_attention_mask=True, return_tensors="pt").to(self.device)
        attention_mask = encoding["attention_mask"][0]
        output = self.model(**encoding)

        # Mean Pooling - Take attention mask into account for correct averaging
        token_embeddings = output[0]  # First element of model_output contains all token embeddings
        input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
        sum_embeddings = torch.sum(token_embeddings * input_mask_expanded, 1)
        sum_mask = torch.clamp(input_mask_expanded.sum(1), min=1e-9)

        sentence_embedding = (sum_embeddings / sum_mask)
        numpy_embedding = sentence_embedding.detach().cpu().numpy()
        numpy_embedding.resize((768,))
        return numpy_embedding

    def return_hyper_params(self):
        """returns hyperparameters for this embedding model
                """
        hyper_params = {"Model name": self.model_name,
                        "Padding Strategies": self.tokenizer._get_padding_truncation_strategies(),
                        "Tokenizer": self.tokenizer}
        return hyper_params
