import subprocess
import os
import shutil


class TarExtractor:
    def __init__(self, dataset_folder_path: str, extract_folder_path: str = "") -> None:
        self.extract_folder_path = extract_folder_path
        self.dataset_folder_path = dataset_folder_path

    def create_extract_folder_path(self) -> None:
        if not os.path.exists(self.extract_folder_path) and self.extract_folder_path != "":
            os.mkdir(self.extract_folder_path)
        if not os.path.exists(self.extract_folder_path + self.dataset_folder_path) and self.dataset_folder_path != "":
            os.mkdir(self.extract_folder_path + self.dataset_folder_path)

