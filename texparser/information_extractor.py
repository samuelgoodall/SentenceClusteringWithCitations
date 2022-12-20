import os
import sys

sys.path.append('../')
from bibitem_parsing.bibitem_parser import BibitemParser


class InformationExtractor:
    extracted_information = {
        "available_papers": 0,
        "pdf_only": 0,
        "tex_file_available": 0,
        "tex_file_with_cite_available": 0,
        "bib_file_available": 0,
        "related_work": 0,
        "last_paper": "",
        "number_of_citations": 0,
        "number_of_usable_citations": 0,
        "all_prerequisites": 0
    }

    def __init__(self):
        self.author_title_tuples_failed = list()
        self.author_title_tuples = list()

    __cite_symbol = "\cite"
    __related_work_symbols = ["\section{Related Work", "\section{Theoretical Background", "\section{Background",
                              "\section{Theory", "\section{Overview",
                              "\section{Literature Review", "\section{Relevant Research",
                              "\section{Literatur Comparison", "\section{Preliminaries"]

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
                    with open(absolute_file_path, 'r') as file:
                        try:
                            complete_file_string = file.read()
                            has_tex_with_cite = has_tex_with_cite or self.__cite_symbol in complete_file_string
                            for related_work_symbol in self.__related_work_symbols:
                                has_related_work = has_related_work or related_work_symbol in complete_file_string
                        except UnicodeDecodeError:
                            pass
            if has_tex:
                self.extracted_information["tex_file_available"] += 1
            if has_tex_with_cite:
                self.extracted_information["tex_file_with_cite_available"] += 1
            if has_related_work:
                self.extracted_information["related_work"] += 1
            if has_bib:
                self.extracted_information["bib_file_available"] += 1
            if has_tex and has_tex_with_cite and has_related_work and (has_bib or has_bbl):
                self.extracted_information["all_prerequisites"] += 1

                php_convertion_script_file = '/mnt/c/Users/sgoodall/Desktop/archive/NLPProjekt/bibitem_parsing/php_script_tex2bib/index.php'
                bibitemparser = BibitemParser(php_convertion_script_file)

                if has_bbl:
                    author_title_tuples = bibitemparser.convert_texfile_2_author_title_tuples(
                        tex_input_file=os.path.join(absolute_paper_path, bbl_file_name))
                    accepted, citation_count, author_title_tuples_cleaned, author_title_tuples_failed = bibitemparser.check_how_many_titles_are_usable(
                        author_title_tuple_list=author_title_tuples)

                    self.extracted_information["number_of_citations"] += citation_count
                    self.extracted_information["number_of_usable_citations"] += accepted
                    self.author_title_tuples += author_title_tuples_cleaned
                    self.author_title_tuples_failed += author_title_tuples_failed
