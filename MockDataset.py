import csv

from torch.utils.data import DataLoader, Dataset

from qualitative_information_extractor import qualitativeInformationExtractor


class MockDataset(Dataset):

    def __init__(self, csv_file: str):
        filename = open(csv_file, "r", encoding = "utf8")
        file = csv.DictReader(filename)
        self.sentences = []
        for col in file:
            self.sentences.append(col['sentence'])
    def __getitem__(self, index):
        return self.sentences[index]

    def __len__(self):
        return len(self.sentences)
    

