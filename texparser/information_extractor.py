import os
import sys


class InformationExtractor:
    extracted_information = {
        "available_papers": 0,
        "pdf_only": 0,
        "tex_file_available": 0,
        "tex_file_with_cite_available": 0,
        "bib_file_available": 0,
        "bbl_file_available": 0,
        "related_work": 0,
        "last_paper": "",
        "all_prerequisites": 0,
        "related_work_length_total" : 0,
        "related_work_length_mean": 0,
        "related_work_length_max": -1,
        "related_work_length_min":  -1
    }
    __cite_symbol = "\cite"
    __related_work_symbols = ["\section{Related Work}", "\section{Theoretical Background}", "\section{Background}", "\section{Theory}", "\section{Overview}",
                              "\section{Literature Review}", "\section{Relevant Research}", "\section{Literatur Comparison}", "\section{Preliminaries}", 
                              "\section{Related Works}", "\section{Previous Work}", "\section{Literature}", "\section{State of the Art}", "\section{Current State of Research}",
                              "\section{Relation to Prior Work}", "\section{Background and Related Work}",
                              "\section{Technical Background}", "\section{Related Work and Background}", "\section{Related Literature}", "\section{Review of Previous Methods}"]

    def extract_all(self, folder_path: str) -> dict:
        for paper in os.listdir(folder_path):
            absolute_paper_path = folder_path + "/" + paper
            self.check_pdf(paper)
            self.check_and_handle_folder(absolute_paper_path)
        return self.extracted_information

    def check_pdf(self, paper: str) -> None:
        if paper.endswith(".pdf"):
            self.extracted_information["pdf_only"] = self.extracted_information["pdf_only"] + 1
            self.extracted_information["available_papers"] += 1

    def length_related_work(self, complete_file_string: str, related_work_symbol_position:int):
        if (related_work_symbol_position != -1 and complete_file_string != ""):
            end_section = complete_file_string.find("\section{", related_work_symbol_position + 1)
            if end_section == -1:
                length_related_work = len(complete_file_string) - related_work_symbol_position
            else:
                length_related_work = end_section - related_work_symbol_position
            self.extracted_information["related_work_length_total"] += length_related_work
            return length_related_work
        else:
            return -1

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
            for file_name in os.listdir(absolute_paper_path):
                if file_name.endswith(".bib"):
                    has_bib = True
                if file_name.endswith("bbl"):
                    has_bbl = True
                if file_name.endswith(".tex"):
                    has_tex = True
                    absolute_file_path = absolute_paper_path + "/" + file_name
                    try:
                        with open(absolute_file_path, 'r') as file:
                            try:
                                complete_file_string = file.read()
                                has_tex_with_cite = has_tex_with_cite or self.__cite_symbol in complete_file_string
                                for related_work_symbol in self.__related_work_symbols:
                                    related_work_symbol_position = complete_file_string.find(related_work_symbol)
                                    if(related_work_symbol_position != -1):
                                        has_related_work = True
                                        length_related_work = self.length_related_work(complete_file_string, related_work_symbol_position)
                                        self.max_length_related_work(length_related_work)
                                        self.min_length_related_work(length_related_work)
                                        self.mean_length_related_work(length_related_work)
                                        break
                            except UnicodeDecodeError:
                                sys.stderr.write("Error message: Contains none unicode characters.\n")
                            except IsADirectoryError:
                                sys.stderr.write("Error message: Is a directory.\n")
                    except FileNotFoundError:
                        sys.stderr.write("Error message: File does not exist.\n")
                        pass
                    except PermissionError:
                        sys.stderr.write("Error message: Access denied.\n")
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
