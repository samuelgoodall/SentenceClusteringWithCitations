import subprocess
import os
import shutil


class TarExtractor:
    def __init__(self, dataset_folder_path: str, extract_folder_path: str = "") -> None:
        self.extract_folder_path = extract_folder_path
        self.dataset_folder_path = dataset_folder_path

