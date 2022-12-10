import os


class InformationExtractor:
    extracted_information = {
        "available_papers": 0,
        "pdf_only": 0,
        "tex_file_available": 0,
        "tex_file_with_cite_available": 0,
        "bib_file_available": 0,
        "related_work": 0,
        "last_paper": "",
        "all_prerequisites": 0
    }
    __cite_symbol = "\cite"
    __related_work_symbols = ["\section{Related Work", "\section{Theoretical Background", "\section{Background", "\section{Theory", "\section{Overview",
                              "\section{Literature Review", "\section{Relevant Research", "\section{Literatur Comparison", "\section{Preliminaries"]
