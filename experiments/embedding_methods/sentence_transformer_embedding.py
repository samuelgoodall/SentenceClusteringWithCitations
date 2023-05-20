from sentence_transformers import SentenceTransformer

from experiments.embedding_methods.local_embedding import LocalEmbedding


class SentenceTransformerEmbedding(LocalEmbedding):

    def __init__(self, model_name: str):
        """
        Parameters
        ----------
        model_name : str
            The name of the model used
        """
        self.model = SentenceTransformer(model_name)
        self.model.max_seq_length = 128
        self.model_name = model_name

    def embed_sentence(self, sentence: str):
        """
        Embeds the words in a sentence using the Sentence Transformers package (sentence_transformer)
        ----------
        sentence : str
            the string that is to be embedded
        """
        sentence = sentence.lower()
        # Sentences are encoded by calling model.encode()
        embedding = self.model.encode(sentence)
        return embedding

    def return_hyper_params(self):
        """
        returns hyperparameters for this embedding model
        """
        hyper_params = {"embedding_dimension": self.model.get_sentence_embedding_dimension(),
                        "model_name": self.model_name,
                        "tokenizer": type(self.model.tokenizer).__name__,
                        "maxSequenceLenght": self.model.max_seq_length}
        return hyper_params
