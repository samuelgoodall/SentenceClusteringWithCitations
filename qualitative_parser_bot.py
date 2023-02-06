import csv
import json
import os
from multiprocessing import Process

import numpy as np
from tqdm import tqdm

from qualitative_information_extractor import QualitativeInformationExtractor


class QualitativeParserBot:
    def __init__(self, dataset_folder_path, output_folder) -> None:
        self.dataset_folder_path = dataset_folder_path
        self.informationExtractor = QualitativeInformationExtractor()
        self.output_folder = output_folder
    
    def function_for_process(self, paper_folder_paths: list, output_file: str, backup_file: str):
        for count, foldername in enumerate(tqdm(paper_folder_paths)):
            self.log_progress(foldername, backup_file)
            self.informationExtractor.fill_data_set(foldername, output_file, False)
    
    def run(self):
        foldernames = os.listdir(self.dataset_folder_path)
        paper_folder_paths = list(map(lambda foldername: os.path.join(self.dataset_folder_path, foldername), foldernames))
        #self.function_for_process(paper_folder_paths, os.path.join(self.output_folder, "data" + ".csv"))
        split_of_paper_folder_path_list = np.array_split(np.array(paper_folder_paths), 8)        
        processes = []
        for i in range(8):
            processes.append(Process(target = self.function_for_process, args = (split_of_paper_folder_path_list[i], os.path.join(self.output_folder, "data" + str(i) + ".csv"), os.path.join(self.output_folder, "backup" + str(i) + ".txt"))))
        for p in processes:
            p.start()
        for p in processes:
            p.join()
        
    def log_progress(self, last_folder: str, output_file) -> None:
        with open(output_file, "a") as backup_file:
            backup_file.write(last_folder + "\n")
        with open("save.json", "w") as backup_file:
            backup_file.writelines(json.dumps(last_folder, indent=7))


if __name__ == "__main__":
    qualitative_parser = QualitativeParserBot("usable_dataset/", "output/")
    print("Parser started")
    qualitative_parser.run()
