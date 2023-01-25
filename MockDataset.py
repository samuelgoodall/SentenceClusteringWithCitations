from torch.utils.data import Dataset, DataLoader
from qualitative_information_extractor import qualitativeInformationExtractor


class MockDataset(Dataset):

    def __init__(self):
        extractor = qualitativeInformationExtractor()
        self.paper = qualitativeInformationExtractor.fill_data_set(extractor, "texparser/")
        print(qualitativeInformationExtractor)

    def __getitem__(self, index):
        return self.paper[index]

    def __len__(self):
        return len(self.paper)
