import csv
import json
import os

from tqdm import tqdm

from qualitative_information_extractor import QualitativeInformationExtractor


class QualitativeParserBot:
    def __init__(self, dataset_folder_path) -> None:
        self.dataset_folder_path = dataset_folder_path
        self.informationExtractor = QualitativeInformationExtractor()

    def run(self):
        filenames = os.listdir(self.dataset_folder_path)
        for count, filename in enumerate(tqdm(filenames)):
            paper_folder_path = os.path.join(self.dataset_folder_path, filename)
            self.informationExtractor.fill_data_set(paper_folder_path)
            self.log_progress(self.informationExtractor.sentence_dataset, count)
        return self.informationExtractor.sentence_dataset

    def log_progress(self, data: list, count: int) -> None:
        if count % 20 == 0:
            with open("backup.json", "a") as backup_file:
                backup_file.writelines(json.dumps(data, indent=7))
            with open("save.json", "w") as backup_file:
                backup_file.writelines(json.dumps(data, indent=7))


if __name__ == "__main__":
    qualitative_parser = QualitativeParserBot("usable_dataset/")
    print("Parser started")
    qualitative_parser.run()
    # Open a file for writing
    with open('data.csv', 'w', newline='') as f:
    # Create a CSV writer
        writer = csv.DictWriter(f, fieldnames=qualitative_parser.informationExtractor.sentence_dataset[0].keys())
        writer.writeheader()
        for row in qualitative_parser.informationExtractor.sentence_dataset:
            writer.writerow(row)