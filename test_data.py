from torch.utils.data import Dataset, DataLoader


class TestDataset(Dataset):

    def __init__(self):
        paper = open(r"C:\Users\Tugce\OneDrive\Belgeler\papertry.txt")
        content = paper.read()
        content = content.split(".")
        self.paper = content
        size = len(content)
        paper.close()

    def __getitem__(self, item):
        return self.paper[item]

    def __len__(self):
        return len(self.paper)


dataset = TestDataset()
print(type(dataset))
dataloader = DataLoader(dataset=dataset, batch_size=10, shuffle=False)

train_embeddings = next(iter(dataloader))
print(type(train_embeddings))
