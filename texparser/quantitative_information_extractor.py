import os
import sys

from information_extractor import InformationExtractor

from bibitem_parsing.algorithmEnum import Algorithm
from bibitem_parsing.bibitem_parser import BibitemParser


class QuantitativeInformationExtractor(InformationExtractor):

    def __init__(self):
        self.author_title_tuples_failed = list()
        self.author_title_tuples = list()

    def extract_all(self, folder_path: str) -> tuple:
        for paper in os.listdir(folder_path):
            absolute_paper_path = folder_path + "/" + paper
            self.check_pdf(paper)
            self.check_and_handle_folder(absolute_paper_path)
        return self.extracted_information, self.author_title_tuples, self.author_title_tuples_failed

    def check_pdf(self, paper: str) -> None:
        if paper.endswith(".pdf"):
            self.extracted_information["pdf_only"] = self.extracted_information["pdf_only"] + 1
            self.extracted_information["available_papers"] += 1


    def max_length_related_work(self, length_related_work: int):
        if (self.extracted_information["related_work_length_max"]) == -1 or (self.extracted_information["related_work_length_max"]) < length_related_work:
            self.extracted_information["related_work_length_max"] = length_related_work

    def min_length_related_work(self, length_related_work: int):
        if (self.extracted_information["related_work_length_min"]) == -1 or (self.extracted_information["related_work_length_max"]) > length_related_work:
            self.extracted_information["related_work_length_min"] = length_related_work

    def mean_length_related_work(self, length_related_work: int):
        if length_related_work != -1:
            total = self.extracted_information["related_work_length_total"]
            counter = self.extracted_information["related_work"] + 1
            self.extracted_information["related_work_length_mean"] = total / counter

    def check_and_handle_folder(self, absolute_paper_path: str) -> None:
        if os.path.isdir(absolute_paper_path):
            self.extracted_information["last_paper"] = absolute_paper_path
            self.extracted_information["available_papers"] += 1
            has_tex = False
            has_tex_with_cite = False
            has_related_work = False
            has_bib = False
            has_bbl = False
            bbl_file_name = None
            for file_name in os.listdir(absolute_paper_path):
                if file_name.endswith(".bib"):
                    has_bib = True
                if file_name.endswith("bbl"):
                    has_bbl = True
                    bbl_file_name = file_name
                if file_name.endswith(".tex"):
                    has_tex = True
                    absolute_file_path = absolute_paper_path + "/" + file_name
                    try:
                        with open(absolute_file_path, 'r') as file:
                            try:
                                complete_file_string = file.read()
                                print(complete_file_string)
                                has_tex_with_cite = has_tex_with_cite or self._cite_symbol in complete_file_string
                                for related_work_symbol in self._related_work_symbols:
                                    related_work_symbol_position = complete_file_string.find(related_work_symbol)
                                    if related_work_symbol_position != -1:
                                        has_related_work = True
                                        length_related_work = self.length_related_work(complete_file_string, related_work_symbol_position)
                                        self.max_length_related_work(length_related_work)
                                        self.min_length_related_work(length_related_work)
                                        self.mean_length_related_work(length_related_work)
                                        break
                            except UnicodeDecodeError:
                                sys.stderr.write("Error message: Contains none unicode characters.\n")
                                pass
                    except FileNotFoundError:
                        sys.stderr.write("Error message: File does not exist.\n")
                        pass
                    except PermissionError:
                        sys.stderr.write("Error message: Access denied.\n")
                        pass
                    except IsADirectoryError:
                        sys.stderr.write("Error message: Is a directory. \n")
                        pass
            if has_tex:
                self.extracted_information["tex_file_available"] += 1
            if has_tex_with_cite:
                self.extracted_information["tex_file_with_cite_available"] += 1
            if has_related_work:
                self.extracted_information["related_work"] += 1
            if has_bib:
                self.extracted_information["bib_file_available"] += 1
            if has_bbl:
                self.extracted_information["bbl_file_available"] += 1
            if has_tex and has_tex_with_cite and has_related_work and (has_bib or has_bbl):
                self.extracted_information["all_prerequisites"] += 1

                php_convertion_script_file = 'bibitem_parsing/php_script_tex2bib/index.php'
                bibitemparser = BibitemParser(php_convertion_script_file)

                if has_bbl:
                    try:
                        author_title_tuples = bibitemparser.convert_texfile_2_author_title_tuples(
                            tex_input_file=os.path.join(absolute_paper_path, bbl_file_name),
                            algorithm=Algorithm.Bib2Tex)
                        accepted, citation_count, author_title_tuples_cleaned, author_title_tuples_failed = bibitemparser.check_how_many_titles_are_usable(
                            author_title_tuple_list=author_title_tuples)

                        self.extracted_information["number_of_citations"] += citation_count
                        self.extracted_information["number_of_usable_citations"] += accepted
                        self.author_title_tuples += author_title_tuples_cleaned
                        self.author_title_tuples_failed += author_title_tuples_failed
                    except UnicodeDecodeError:
                        pass
