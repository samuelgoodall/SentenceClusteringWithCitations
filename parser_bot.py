import json
import os
import shutil

from tqdm import tqdm

from texparser.information_extractor import InformationExtractor
from texparser.tar_extractor import TarExtractor


class ParserBot:
    def __init__(self, dataset_folder_path, extract_folder_path: str = "") -> None:
        self.dataset_folder_path = dataset_folder_path
        self.extract_folder_path = extract_folder_path
        self.tarExtractor = TarExtractor(
            self.dataset_folder_path, self.extract_folder_path)
        self.informationExtractor = InformationExtractor()

    def run(self):
        self.tarExtractor.create_extract_folder_path()
        filenames = os.listdir(self.dataset_folder_path)
        for count, filename in enumerate(tqdm(filenames)):
            try:
                self.tarExtractor.untar_file_into_folder(
                    self.dataset_folder_path + filename)
            except Exception as e:
                print(e)
            extract_folder = self.extract_folder_path + \
                self.dataset_folder_path + filename.replace(".tar", "")
            sub_extract_folder = extract_folder + \
                "/" + os.listdir(extract_folder)[0]
            self.tarExtractor.extract_folder(
                sub_extract_folder, self.tarExtractor.untargz_file_into_folder)[1]
            data = self.informationExtractor.extract_all(sub_extract_folder)
            self.log_progress(data, count)
            shutil.rmtree(extract_folder)
        self.tarExtractor.delete_extract_folder_path()

    def log_progress(self, data: dict, count: int) -> None:
        if count % 20 == 0:
            with open("backup.json", "a") as backup_file:
                backup_file.writelines(json.dumps(data, indent=7))
            with open("save.json", "w") as backup_file:
                backup_file.writelines(json.dumps(data, indent=7))


if __name__ == "__main__":
    parser = ParserBot("content/", "extract/")
    print("Parser started")
    parser.run()
