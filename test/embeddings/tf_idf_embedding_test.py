import unittest
from experiments.embedding_methods.tf_idf_embedding import TfIdfEmbedding

class TfIdfEmbeddingTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        super(TfIdfEmbeddingTest, cls).setUpClass()
        cls.tfIdfEmbedding = TfIdfEmbedding()
        
    
    def test_lemmatise_sentence__stringInput_lemmitisedString(self):
        # arrange
        test_input = "There are other test sentences"

        # act
        output = self.tfIdfEmbedding.lemmatise_sentence(test_input)

        # assert
        self.assertIsNotNone(output)
        self.assertEqual(output, "there be other test sentence")
    
    def test_embed_sentence__stringInput_embedding_vector(self):
        # arrange
        test_input = ["This is a test sentence", "There are other test sentences", "This is a third sentence"]

        # act
        output = self.tfIdfEmbedding.embed_sentences(test_input)
        print(output)
        
        # assert
        self.assertIsNotNone(output)
        