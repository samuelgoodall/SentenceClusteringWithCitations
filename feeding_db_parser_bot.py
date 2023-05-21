import os

from tqdm import tqdm
from qualitative_information_extractor_database import QualitativeInformationExtractorDatabase

class FeedingDBParserBot:
    def __init__(self, dataset_folder_path) -> None:
        self.dataset_folder_path = dataset_folder_path
        abs_datasetdb_path = os.path.abspath("dataset/database/dataset.db")
        self.informationExtractor = QualitativeInformationExtractorDatabase(abs_datasetdb_path)

    def run(self):
        foldernames = os.listdir(self.dataset_folder_path)
        paper_folder_paths = list(
            map(lambda foldername: os.path.join(self.dataset_folder_path, foldername), foldernames))

        for count, foldername in enumerate(tqdm(paper_folder_paths)):
            self.informationExtractor.fill_data_set(foldername, False)


if __name__ == "__main__":
    print("PATH",os.path.abspath("../usable_dataset"))
    "../../usable_dataset/"
    qualitative_parser = FeedingDBParserBot("../usable_dataset")

    print("Parser started")
    qualitative_parser.run()