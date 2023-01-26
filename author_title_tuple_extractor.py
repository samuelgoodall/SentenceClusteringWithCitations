import json
import multiprocessing as mp
import os
from multiprocessing import Process

import numpy
from tqdm import tqdm

from bibitem_parsing.algorithmEnum import Algorithm
from bibitem_parsing.bibitem_parser import BibitemParser

"""
Skript for going over the extracted Dataset and extracting the Author title tuples does so with utilizing multiple threads
"""
class ExtractedParserBot:
    def __init__(self, dataset_folder_path, paper_to_start: str = None) -> None:
        self.paper_to_start = paper_to_start
        self.dataset_folder_path = dataset_folder_path
        self.bibitem_parser = BibitemParser()
        if not os.path.exists("author_title_tuples"):
            print("creating_author_title_tuples")
            os.makedirs("author_title_tuples")
        self.author_title_tuples_output_folder = "author_title_tuples"

    def iterate_over_dataset(self, filenames, process_id):
        print("PROCESS", process_id)
        found_start_paper = (self.paper_to_start is None)
        dataset_len = 0
        for count, paper_folder in enumerate(tqdm(filenames)):
            if (not found_start_paper) and paper_folder == self.paper_to_start:
                print("found_startpaper:", paper_folder)
                found_start_paper = True
            if found_start_paper:
                abs_paper_folder_path = os.path.join(os.path.abspath(self.dataset_folder_path), paper_folder)
                for filename in (os.listdir(abs_paper_folder_path)):
                    abs_file_path = os.path.abspath(os.path.join(abs_paper_folder_path, filename))
                    author_title_tuples = self.bibitem_parser.convert_texfile_2_author_title_tuples(abs_file_path,
                                                                                                    Algorithm.Bib2Tex)
                    if filename.endswith(".bbl"):
                        paper_json_output_folder = os.path.join(self.author_title_tuples_output_folder, paper_folder)
                        if not os.path.exists(paper_json_output_folder):
                            os.makedirs(paper_json_output_folder)
                        json_filename = filename.split(".bbl")[0] if filename.endswith(".bbl") else \
                            filename.split(".bib")[0]
                        json_filename += ".json"
                        path = os.path.join(self.author_title_tuples_output_folder, paper_folder, json_filename)
                        dataset_len += len(author_title_tuples)
                        with open(path, "w") as author_title_tuples_json:
                            author_title_tuples_json.writelines(json.dumps(author_title_tuples, indent=7))
        dataset_stats_path = os.path.join(self.author_title_tuples_output_folder,
                                          "dataset_stats" + str(process_id) + ".json")
        with open(dataset_stats_path, "w") as dataset_stats:
            dataset_stats.writelines(json.dumps({"dataset_length": dataset_len}))

    def run(self):
        cpu_count = mp.cpu_count()
        print("availableCPU", cpu_count)
        cpu_used_count = cpu_count if 6 > cpu_count else 6
        filenames = os.listdir(self.dataset_folder_path)
        process_items_array = numpy.array_split(numpy.asarray(filenames), cpu_used_count)

        processes = []
        for i in range(cpu_used_count):
            processes.append(Process(target=self.iterate_over_dataset, args=(process_items_array[i], i)))

        for p in processes:
            p.start()

        for p in processes:
            p.join()

        return


if __name__ == "__main__":
    parser = ExtractedParserBot("usable_dataset/")
    print("Parser started")
    parser.run()
