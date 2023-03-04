import unittest

from experiments.experiment_glove_embeddings import convert_sentence_2_glove_embedding, get_glove_embeddings_keyed_vectors


class GloveEmbeddingsTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """ get_some_resource() is slow, to avoid calling it for each test use setUpClass()
            and store the result as class variable
        """
        super(GloveEmbeddingsTest, cls).setUpClass()
        glove_embeddings_path = "../../embeddings/glove/glove.840B.300d.txt" #"../../embeddings/glove/glove.6B/glove.6B.50d.txt"
        cls.glove_embeddings_dimension = 300
        cls.glove_embeddings_dict = get_glove_embeddings_keyed_vectors(glove_embeddings_path)

    def setUp(self) -> None:
        print("setup")

    def tearDown(self) -> None:
        print("teardown")

    def test_convert_sentence_2_glove_embedding__stringInput_embedding_vector(self):
        # arrange
        test_input = "Low-Rank Pairwise Alignment Bilinear Network For Few-Shot Fine-Grained Image Classification"

        # act
        output = convert_sentence_2_glove_embedding(test_input,
                                                    GloveEmbeddingsTest.glove_embeddings_dict,
                                                    GloveEmbeddingsTest.glove_embeddings_dimension)

        # assert
        self.assertIsNotNone(output)