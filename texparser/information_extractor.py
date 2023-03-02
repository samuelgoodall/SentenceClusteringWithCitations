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
        "number_of_citations": 0,
        "number_of_usable_citations": 0,
        "all_prerequisites": 0,
        "related_work_length_total" : 0,
        "related_work_length_mean": 0,
        "related_work_length_max": -1,
        "related_work_length_min":  -1
    }

    def __init__(self):
        self.author_title_tuples_failed = list()
        self.author_title_tuples = list()

    _cite_symbol = "\cite"
    _related_work_symbols = ["\section{Related Work}", "\section{Theoretical Background}", "\section{Background}", "\section{Theory}", "\section{Overview}",
                              "\section{Literature Review}", "\section{Relevant Research}", "\section{Literatur Comparison}", "\section{Preliminaries}",
                              "\section{Related Works}", "\section{Previous Work}", "\section{Literature}", "\section{State of the Art}", "\section{Current State of Research}",
                              "\section{Relation to Prior Work}", "\section{Background and Related Work}",
                              "\section{Technical Background}", "\section{Related Work and Background}", "\section{Related Literature}", "\section{Review of Previous Methods}"]

    def length_related_work(self, complete_file_string: str, related_work_symbol_position:int):
        if related_work_symbol_position != -1 and complete_file_string != "":
            end_section = complete_file_string.find("\section{", related_work_symbol_position + 1)
            if end_section == -1:
                length_related_work = len(complete_file_string) - related_work_symbol_position
            else:
                length_related_work = end_section - related_work_symbol_position
            self.extracted_information["related_work_length_total"] += length_related_work
            return length_related_work
        else:
            return -1
        