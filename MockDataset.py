from torch.utils.data import Dataset, DataLoader
from qualitative_information_extractor import qualitativeInformationExtractor


class MockDataset(Dataset):

    def __init__(self):
        extractor = qualitativeInformationExtractor()
        qualitativeInformationExtractor.fill_data_set(extractor, "texparser/")
        self.paper = extractor.sentence_dataset

    def __getitem__(self, item):
        return self.paper[item]

    def __len__(self):
        return len(self.paper)

