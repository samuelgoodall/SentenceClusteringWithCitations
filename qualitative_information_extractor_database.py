import os
import sys

from dataset.database.database import (Citation, Paper, Paragraph, Sentence,
                                       SQAlchemyDatabase)
from qualitative_information_extractor import QualitativeInformationExtractor


class QualitativeInformationExtractorDatabase(QualitativeInformationExtractor):

    def __init__(self, db_path: str):
        super().__init__()
        print("db_path", db_path)
        self.sql_session = SQAlchemyDatabase(db_path).session()

    def add_new_paper(self, paper_title="", paper_authors=""):
        paper = (
            self.sql_session.query(Paper)
            .filter(Paper.title == paper_title)
            .one_or_none()
        )
        if paper is not None:
            return paper

        paper = Paper(title=paper_title, authors=paper_authors)
        return paper

    def create_new_paragraph(self, paper: Paper):
        new_paragraph = Paragraph()
        new_paragraph.paper = paper
        return new_paragraph

    def create_new_sentence(self, new_paragraph, sentence_content: str):
        new_sentence = Sentence(content=sentence_content)
        new_sentence.paragraph = new_paragraph
        return new_sentence

    def create_new_citation(self, title:str, author:str, abstract:str,new_sentence:Sentence):
        new_citation = Citation(title=title,author=str(author),abstract=abstract)
        new_sentence.citations.append(new_citation)
        return new_citation

    def fill_data_set(self, paper_folder_path: str,  include_bbl: bool):
        not_found_right_tex = True
        for file_name in os.listdir(str(paper_folder_path)):
            if file_name.endswith(".tex") & not_found_right_tex:
                absolute_paper_path = os.path.join(paper_folder_path, file_name)
                try:
                    with open(absolute_paper_path, 'r', encoding="utf-8") as file:
                        try:
                            complete_file_string = file.read()
                            if self.get_related_work_beginning(complete_file_string) != -1:
                                not_found_right_tex = False
                                bibliography_path = self.check_bibliography_type(paper_folder_path)
                                if bibliography_path.endswith(".bib"):
                                    bib_data = self.initialize_bib_parser(bibliography_path)
                                elif include_bbl is False:
                                    break
                                paper_parsed_paragraphs = []
                                related_work_string = self.get_related_work(complete_file_string)
                                paragraphs = self.get_paragraphs(related_work_string)
                                for index, paragraph in enumerate(paragraphs):
                                    citation_paragraph_end = self.find_citations_paragraph_end(paragraph)
                                    paragraphs[index] = self.delete_citation_paragraph_end(paragraph,
                                                                                           citation_paragraph_end)
                                    paragraph_parsed_sentences = []

                                    sentences = self.get_sentences(paragraphs[index])
                                    for index, sentence in enumerate(sentences):
                                        sentences[index] = self.put_citation_paragraph_end_in_sentence(sentence,
                                                                                                       citation_paragraph_end)
                                    clean_sentences = self.delete_without_citations(sentences)

                                    for count, sentence in enumerate(clean_sentences):
                                        if self.compile_latex_to_text(sentence) == "":
                                            continue

                                        citations_list = self.get_citation_keywords(sentence)

                                        processed_citations_list = []
                                        if bibliography_path.endswith(".bib"):
                                            at_least_one_title_available = False
                                            for citation in citations_list:
                                                titel, author, abstract = self.find_titel_for_citation_bib(citation,
                                                                                                           bib_data)
                                                if titel is not None:
                                                    titel = self.clean_titel(titel)
                                                    if titel != "":
                                                        processed_citations_list.append((titel, author, abstract))
                                                        at_least_one_title_available = True
                                            if at_least_one_title_available:
                                                new_sentence = Sentence(content=self.compile_latex_to_text(
                                                                                          sentence))
                                                for citation in processed_citations_list:
                                                    new_title, new_author, new_abstract = citation
                                                    self.create_new_citation(new_title, new_author,
                                                                             new_abstract, new_sentence)
                                                paragraph_parsed_sentences.append(new_sentence)

                                    if len(paragraph_parsed_sentences) > 0:
                                        new_paragraph = Paragraph()
                                        for sentence in paragraph_parsed_sentences:
                                            sentence.paragraph = new_paragraph
                                        paper_parsed_paragraphs.append(new_paragraph)
                                if len(paper_parsed_paragraphs) > 0:
                                    new_paper = self.add_new_paper(paper_title=paper_folder_path, paper_authors="")
                                    for paragaph in paper_parsed_paragraphs:
                                        paragaph.paper= new_paper
                                    self.sql_session.add(new_paper)
                                    self.sql_session.commit()

                        except UnicodeDecodeError:
                            sys.stderr.write("Error message: Contains none unicode characters.\n")
                except FileNotFoundError:
                    sys.stderr.write("Error message: File does not exist.\n")
                except PermissionError:
                    sys.stderr.write("Error message: Access denied.\n")
                except IsADirectoryError:
                    sys.stderr.write("Error message: Is a directory. \n")


