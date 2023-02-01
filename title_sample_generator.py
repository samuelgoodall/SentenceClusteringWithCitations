import json
import os
import random as rand

import numpy as np

from bibitem_parsing.algorithmEnum import Algorithm
from bibitem_parsing.bibitem_parser import BibitemParser


def main(dataset_folder_path: str):
    bibitem_parser = BibitemParser()

    paper_paths = os.listdir(dataset_folder_path)
    abs_paper_paths = list(map(lambda paper_folder: os.path.join(os.path.abspath(dataset_folder_path), paper_folder),
                               paper_paths))

    # get all papers with bbl files
    bbl_paper_paths = []
    for paper_path in abs_paper_paths:
        for filename in (os.listdir(str(paper_path))):
            if filename.endswith(".bbl"):
                bbl_paper_paths.append(paper_path)

    print(len(bbl_paper_paths))
    paper_sample = np.random.choice(bbl_paper_paths, size=100, replace=False)
    title_examples = []
    for paper_path in paper_sample:
        print("PAPER", paper_path)
        for filename in (os.listdir(str(paper_path))):
            print("FILE:", filename)
            if filename.endswith(".bbl"):
                bbl_paper_paths.append(paper_path)
                abs_file_path = os.path.join(paper_path, filename)
                author_title_tuples = bibitem_parser.convert_texfile_2_author_title_tuples(abs_file_path,
                                                                                           Algorithm.Bib2Tex)
                title_tuples = list(map(lambda tuple: (tuple[0][1], tuple[1]), author_title_tuples))
                title_examples += title_tuples

    results = rand.sample(title_examples, 100)
    with open("results.json", "w") as author_title_tuples_json:
        author_title_tuples_json.writelines(json.dumps(results, indent=7))


if __name__ == "__main__":
    main("usable_dataset/")
