from torch.utils.data import Dataset


class TestDataset(Dataset):

    def __init__(self):
        paper = open(r"C:\Users\Tugce\OneDrive\Belgeler\papertry.txt")
        content = paper.read()
        content = content.split(".")
        self.paper = content
        paper.close()

    def __getitem__(self, item):
        return self.paper[item]


dataset = TestDataset()

print(dataset.paper)
