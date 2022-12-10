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
            for file_name in os.listdir(absolute_paper_path):
                if file_name.endswith(".bib"):
                    has_bib = True
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
            if has_tex and has_tex_with_cite and has_related_work and has_bib:
                self.extracted_information["all_prerequisites"] += 1
