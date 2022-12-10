import subprocess
import os
import shutil


class TarExtractor:
    def __init__(self, dataset_folder_path: str, extract_folder_path: str = "") -> None:
        self.extract_folder_path = extract_folder_path
        self.dataset_folder_path = dataset_folder_path

    def extract_file_into_folder(self, file_name: str, params: str, ending: str) -> tuple:
        tar_process = any
        if file_name.endswith(ending):
            if ending in file_name:
                file_folder_path = self.__create_file_folder_path(
                    file_name, ending)
                process = self.__create_tar_process(
                    params, file_name, file_folder_path)
                return self.__analyse_process(process)
        return (0, 0)

    def __create_file_folder_path(self, file_name: str, ending: str) -> str:
        file_folder_path = file_name.replace(ending, "")
        if not file_folder_path.startswith(self.extract_folder_path):
            file_folder_path = self.extract_folder_path + file_folder_path
        if not os.path.isdir(file_folder_path):
            os.mkdir(file_folder_path)
        return file_folder_path

    def __create_tar_process(self, params: str, file_name: str, file_folder_path: str):
        return subprocess.run(["tar", params, file_name, "--directory", file_folder_path], capture_output=True)

    def __analyse_process(self, process):
        fail_counter, success_counter = 0, 0
        if process.returncode == 0 or process.returncode == 2:
            success_counter = success_counter + 1
        else:
            fail_counter = fail_counter + 1
        return (success_counter, fail_counter)

    def untargz_file_into_folder(self, filename: str):
        return self.extract_file_into_folder(filename, "xf", ".gz")

    def untar_file_into_folder(self, file_name: str):
        return self.extract_file_into_folder(file_name, "xvf", ".tar")

    def create_extract_folder_path(self) -> None:
        if not os.path.exists(self.extract_folder_path) and self.extract_folder_path != "":
            os.mkdir(self.extract_folder_path)
        if not os.path.exists(self.extract_folder_path + self.dataset_folder_path) and self.dataset_folder_path != "":
            os.mkdir(self.extract_folder_path + self.dataset_folder_path)

    def delete_extract_folder_path(self) -> None:
        if os.path.exists(self.extract_folder_path):
            shutil.rmtree(self.extract_folder_path)
