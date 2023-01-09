import os
import shutil
import subprocess
import sys
from pathlib import Path


class TarExtractor:
    def __init__(self, dataset_folder_path: str, extract_folder_path: str = "") -> None:
        self.extract_folder_path = extract_folder_path
        self.dataset_folder_path = dataset_folder_path

    def extract_folder(self, folder, func):
        processes = []
        filenames = os.listdir(folder)
        for filename in filenames:
            try:
                path = Path(folder) / filename
                filename, file_extension = os.path.splitext(path)
                processes.append(func(filename + file_extension))
            except FileExistsError:
                sys.stderr.write("Error message: File already exists. \n")
        return processes
    def _extract_file_into_folder(self, file_name: str, params: str, ending: str) -> tuple:
        tar_process = any
        if file_name.endswith(ending):
            if ending in file_name:
                file_folder_path = self._create_file_folder_path(
                    file_name, ending)
                process = self._create_tar_process(
                    params, file_name, file_folder_path)
                return self._analyse_process(process)
        return (0, 0)

    def _create_file_folder_path(self, file_name: str, ending: str) -> str:
        file_folder_path = file_name.replace(ending, "")
        if not file_folder_path.startswith(self.extract_folder_path):
            file_folder_path = Path(self.extract_folder_path) / file_folder_path
        try:
            if not os.path.isdir(file_folder_path):
                os.mkdir(file_folder_path)
        except FileExistsError:
            sys.stderr.write("Error message: Directory already exists. \n")
        pass
        return file_folder_path

    def _create_tar_process(self, params: str, file_name: str, file_folder_path: str):
        return subprocess.run(["tar", params, file_name, "--directory", file_folder_path], capture_output=True)

    def _analyse_process(self, process):
        fail_counter, success_counter = 0, 0
        if process.returncode == 0 or process.returncode == 2:
            success_counter = success_counter + 1
        else:
            fail_counter = fail_counter + 1
        return (success_counter, fail_counter)

    def untargz_file_into_folder(self, filename: str):
        return self._extract_file_into_folder(filename, "xf", ".gz")

    def untar_file_into_folder(self, file_name: str):
        return self._extract_file_into_folder(file_name, "xvf", ".tar")

    def create_extract_folder_path(self) -> None:
        try:
            if not os.path.exists(self.extract_folder_path) and self.extract_folder_path != "":
                os.mkdir(self.extract_folder_path)
            if not os.path.exists(self.extract_folder_path + self.dataset_folder_path) and self.dataset_folder_path != "":
                os.mkdir(self.extract_folder_path + self.dataset_folder_path)
        except FileExistsError:
            sys.stderr.write("Error message: Directory already exists. \n")
            pass
        except FileNotFoundError:
            sys.stderr.write("Error message: File not found. \n")
            pass

    def delete_extract_folder_path(self) -> None:
        try:
            if os.path.exists(self.extract_folder_path):
                shutil.rmtree(self.extract_folder_path)
        except FileNotFoundError:
            sys.stderr.write("Error message: File is not found. \n")
