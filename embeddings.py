from sentence_transformers import SentenceTransformer
from torch.utils.data import Dataset, DataLoader
from MockDataset import MockDataset

model = SentenceTransformer('all-MiniLM-L6-v2')
sentences = MockDataset()
dataloader = DataLoader(dataset=sentences, batch_size=20, shuffle=True)

train_embeddings = next(iter(dataloader))


sentence_embeddings = model.encode(sentences)

for sentence, embedding in zip(sentences, sentence_embeddings):
    print("Sentence:", sentence)
    print("Embedding:", embedding)
    print("")