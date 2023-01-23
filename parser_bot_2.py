import os

from tqdm import tqdm

from bibitem_parsing.algorithmEnum import Algorithm
from bibitem_parsing.bibitem_parser import BibitemParser
from texparser.information_extractor import InformationExtractor


class ExtractedParserBot:
    def __init__(self, dataset_folder_path, paper_to_start: str = None) -> None:
        self.paper_to_start = paper_to_start
        self.dataset_folder_path = dataset_folder_path
        self.informationExtractor = InformationExtractor(None)
        self.bibitem_parser = BibitemParser()

    def run(self):
        filenames = os.listdir(self.dataset_folder_path)
        found_start_paper = (self.paper_to_start is None)
        for count, paper_folder in enumerate(tqdm(filenames)):
            if (not found_start_paper) and paper_folder == self.paper_to_start:
                print("found_startpaper:", paper_folder)
                found_start_paper = True
            if found_start_paper:
                abs_paper_folder_path = os.path.join(os.path.abspath(self.dataset_folder_path), paper_folder)
                self.informationExtractor.check_and_handle_folder(abs_paper_folder_path, paper_folder)
                for filename in (os.listdir(abs_paper_folder_path)):
                    abs_file_path = os.path.abspath(os.path.join(abs_paper_folder_path, filename))
                    author_title_tuples = self.bibitem_parser.convert_texfile_2_author_title_tuples(abs_file_path,
                                                                                                    Algorithm.Bib2Tex)


if __name__ == "__main__":
    parser = ExtractedParserBot("usable_dataset/")

    print("Parser started")
    parser.run()
