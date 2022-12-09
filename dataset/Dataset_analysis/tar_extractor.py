
import subprocess
import os

class TarExtractor:
    count_pdfs = 0

    def extract_folder(self, folder, func):
        processes = []
        filenames = os.listdir(folder)
        for filename in filenames:
            try:
                processes.append(func(folder + "/" + filename))
            except:
                pass # How should we handle already existing folders?
        return processes

    def extract_file_into_folder(self,file_name:str, params:str, ending:str):
        tar_process = any
        if file_name.endswith(ending):
            if ending in file_name:
                file_folder_path = file_name.replace(ending, "")
                if not os.path.isdir(file_folder_path):
                    os.mkdir(file_folder_path)
                    return subprocess.run(["tar", params, file_name, "--directory", file_folder_path], capture_output=True)
                else:
                    raise Exception(f"Folder already exists: {file_folder_path}")
    
    def untargz_file_into_folder(self, filename):
        return self.extract_file_into_folder(filename, "xf", ".gz")

    def untar_file_into_folder(self, file_name):
        print(file_name)
        return self.extract_file_into_folder(file_name, "xvf", ".tar")

    def analyse_processes(self, processes):
        fail_counter, success_counter = 0,0
        for process in processes:
            if process.returncode == 0 or process.returncode == 2:
                success_counter = success_counter + 1
            else:
                fail_counter = fail_counter + 1
        return (success_counter, fail_counter)

    