from sentence_transformers import SentenceTransformer

from test_data import TestDataset

model = SentenceTransformer('all-MiniLM-L6-v2')
sentences = TestDataset()
sentence_embeddings = model.encode(sentences)

for sentence, embedding in zip(sentences, sentence_embeddings):
    print("Sentence:", sentence)
    print("Embedding:", embedding)
    print("")