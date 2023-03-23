from experiments.embedding_methods.embedding_interface import EmbeddingInterface


class FastTextEmbedding(EmbeddingInterface):
    def __init__(self, embedding_dimension, fasttext_model_path):
        self.embedding_dimension = embedding_dimension
        self.model = fasttext.load_model(fasttext_model_path)
        self.fasttext_model_path = fasttext_model_path

    def embed_sentence(self, sentence: str):
        """
        converts a sentence into fastext embedding

        Parameters
        ----------
        sentence : str
            the string that is to be embedded

        Returns
        -------
        numpy array
            the embedding vector
        """
        sentence_vector = self.model.get_sentence_vector(sentence)

        return sentence_vector

    def return_hyper_params(self):
        """
        returns the hyper params as dict it is dict in order to keep it flexible

        Returns
        -------
        dict
            the hyper_params as a dictionary
        """
        hyper_params = {"embedding_dimension": self.embedding_dimension,
                        "fasttext_model_path": self.fasttext_model_path}
        return hyper_params



import fasttext.util

if __name__ == "__main__":
    fasttext.util.download_model('en', if_exists='ignore')
    ft = fasttext.load_model('embeddings/FastText/cc.en.300.bin')
    wordvector = ft.get_word_vector("e")
    print("DONE")