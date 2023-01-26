import os
import shutil

from texparser.information_extractor import InformationExtractor


class UsablePaperExtractor(InformationExtractor):
    def __init__(self, destination_folder):
        self.destination_folder = destination_folder
        if not os.path.exists(destination_folder):
            print("creating outputfolder for usable dataset at:", destination_folder)
            os.makedirs(destination_folder)

    def copy_usable_paper_folder(self, usable_paper_folder_path: str, paper: str):
        destination_folder_path = self.destination_folder + "/" + paper
        if not os.path.exists(destination_folder_path):
            os.makedirs(destination_folder_path)
        for file_name in os.listdir(usable_paper_folder_path):
            # construct full file path
            source = usable_paper_folder_path + "/" + file_name
            destination = self.destination_folder + "/" + paper + "/" + file_name
            # copy only files
            if os.path.isfile(source) and (
                    file_name.endswith(".bib") or file_name.endswith(".bbl") or file_name.endswith(".tex")):
                shutil.copy(source, destination)

    def check_and_handle_folder(self, absolute_paper_path: str, paper: str) -> bool:
        if super().check_and_handle_folder(absolute_paper_path, paper):
            self.copy_usable_paper_folder(absolute_paper_path, paper)
        return super().check_and_handle_folder(absolute_paper_path, paper)
