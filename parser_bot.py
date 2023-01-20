import json
import os
import shutil

from tqdm import tqdm

from texparser.information_extractor import InformationExtractor
from texparser.tar_extractor import TarExtractor


class ParserBot:
    def __init__(self, file_to_start: str, dataset_folder_path, extract_folder_path: str = "",
                 extract_to_keep_path: str = None) -> None:
        self.file_to_start = file_to_start
        self.dataset_folder_path = dataset_folder_path
        self.extract_folder_path = extract_folder_path
        self.tarExtractor = TarExtractor(
            self.dataset_folder_path, self.extract_folder_path)
        self.informationExtractor = InformationExtractor(extract_to_keep_path)

    def run(self):
        self.tarExtractor.create_extract_folder_path()
        filenames = os.listdir(self.dataset_folder_path)
        found_start_file = (self.file_to_start is None)
        for count, filename in enumerate(tqdm(filenames)):
            if filename == self.file_to_start:
                print("found_startfile:", filename)
                found_start_file = True
            if found_start_file:
                try:
                    self.tarExtractor.untar_file_into_folder(
                        self.dataset_folder_path + filename)
                except Exception as e:
                    print(e)
                extract_folder = self.extract_folder_path + \
                                self.dataset_folder_path + filename.replace(".tar", "")
                sub_extract_folder = extract_folder + \
                                    "/" + os.listdir(extract_folder)[0]
                print("SUBEXTRACT_FOLDER", sub_extract_folder)
                self.tarExtractor.extract_folder(
                    sub_extract_folder, self.tarExtractor.untargz_file_into_folder)[1]
                data = self.informationExtractor.extract_all(
                    sub_extract_folder)
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
    parser = ParserBot(None, "content/", "extract/", "usable_dataset/")

    print("Parser started")
    parser.run()
