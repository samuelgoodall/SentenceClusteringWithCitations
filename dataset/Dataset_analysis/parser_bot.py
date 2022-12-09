from tar_extractor import TarExtractor
from information_extractor import InformationExtractor
import os
import shutil
from tqdm import tqdm
import json

class ParserBot:
    tarExtractor = TarExtractor()
    InformationExtractor = InformationExtractor()

    def __init__(self, root_folder_name) -> None:
        self.root_folder_name = root_folder_name
        
    def run(self):
        filenames = os.listdir(self.root_folder_name)
        for count, filename in enumerate(tqdm(filenames)): 
            try:
                self.tarExtractor.untar_file_into_folder(self.root_folder_name + filename)
            except:
                pass # How should we handle already existing folders?
            subfolder = self.root_folder_name + filename.replace(".tar", "") 
            subsubfolder = subfolder + "/" + os.listdir(subfolder)[0] # Position after tar file is unzipped
            self.tarExtractor.extract_folder(subsubfolder, self.tarExtractor.untargz_file_into_folder)
            data = self.InformationExtractor.extract_all(subsubfolder)
            self.log_progress(data, count)
            shutil.rmtree(subfolder)
    
    def log_progress(self, data, count):
        if count % 20 == 0:
            with open("backup.json", "a") as backup_file:
                backup_file.writelines(json.dumps(data, indent=7))
            with open("save.json", "w") as backup_file:
                backup_file.writelines(json.dumps(data, indent=7))
        
            
if __name__ == "__main__":
    parser = ParserBot("content/")
    print("Parser started")
    parser.run()
