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

    def log_progress(self, data: dict, count: int) -> None:
        if count % 20 == 0:
            with open("backup.json", "a") as backup_file:
                backup_file.writelines(json.dumps(data, indent=7))
            with open("save.json", "w") as backup_file:
                backup_file.writelines(json.dumps(data, indent=7))

