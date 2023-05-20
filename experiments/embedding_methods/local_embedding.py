
from experiments.embedding_methods.embedding_interface import (
    EmbeddingInterface, SentenceCitationFusingMethod)


class LocalEmbedding(EmbeddingInterface):
    def embed_sentences(self, sentences, use_citation):
        bag_of_sentences = []
        for sentence_index, sentence in enumerate(sentences):
            sentence_embedding = self.embed_sentence(sentence.sentence)
            citation_embeddings = []
            if use_citation:
                for citation in sentence.citations:
                    current_citation_embedding = self.embed_sentence(citation.citation_title)
                    citation_embeddings.append(current_citation_embedding)
                overall_embedding = self.fuse_sentence_and_citation_embedding(sentence_embedding,
                                                                     citation_embeddings,
                                                                     SentenceCitationFusingMethod.Averaging)
            else:
                overall_embedding = sentence_embedding
            bag_of_sentences.append(overall_embedding)
        return bag_of_sentences