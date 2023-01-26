from torch.utils.data import Dataset, DataLoader
from qualitative_information_extractor import qualitativeInformationExtractor


class MockDataset(Dataset):

    def __init__(self):
        extractor = qualitativeInformationExtractor()
        extracted = qualitativeInformationExtractor.fill_data_set(extractor, "texparser/")
        self.sentences = list(map(lambda item: item.get("sentence"), extracted))
        print(self.sentences)

    def __getitem__(self, index):
        return self.sentences[index]

    def __len__(self):
        return len(self.sentences)
