import csv
import os
import sys
import uuid

from bibitem_parsing.bibitem_parser import BibitemParser
from database.database import Paper
from qualitative_information_extractor import QualitativeInformationExtractor


class QualitativeInformationExtractorDatabase(QualitativeInformationExtractor):

    def fill_data_set(self, paper_folder_path: str, output_file: str, include_bbl: bool):
        sentence_dataset = []
        for file_name in os.listdir(str(paper_folder_path)):
            if file_name.endswith(".tex"):
                absolute_paper_path = os.path.join(paper_folder_path, file_name)
                try:
                    with open(absolute_paper_path, 'r', encoding="utf-8") as file:
                        try:
                            complete_file_string = file.read()
                            paper_ID = uuid.uuid3(uuid.NAMESPACE_DNS, complete_file_string).urn
                            new_paper = Paper(title="", authors="authors")
                            if self.get_related_work_beginning(complete_file_string) != -1:
                                bibliography_path = self.check_bibliography_type(paper_folder_path)
                                if bibliography_path.endswith(".bib"):
                                    bib_data = self.initialize_bib_parser(bibliography_path)
                                elif include_bbl is False:
                                    break
                                related_work_string = self.get_related_work(complete_file_string)
                                paragraphs = self.get_paragraphs(related_work_string)
                                for index, paragraph in enumerate(paragraphs):
                                    paragraph_ID = uuid.uuid3(uuid.NAMESPACE_DNS, paragraph).urn
                                    citation_paragraph_end = self.find_citations_paragraph_end(paragraph)
                                    paragraphs[index] = self.delete_citation_paragraph_end(paragraph,
                                                                                           citation_paragraph_end)
                                    sentences = self.get_sentences(paragraphs[index])
                                    for index, sentence in enumerate(sentences):
                                        sentences[index] = self.put_citation_paragraph_end_in_sentence(sentence,
                                                                                                       citation_paragraph_end)
                                    clean_sentences = self.delete_without_citations(sentences)
                                    for count, sentence in enumerate(clean_sentences):
                                        sentence_ID = uuid.uuid3(uuid.NAMESPACE_DNS, sentence).urn
                                        citations_list = self.get_citation_keywords(sentence)
                                        clean_sentences[count] = self.compile_latex_to_text(sentence)
                                        citation_titel_list = []
                                        citation_author_list = []
                                        citation_abstract_list = []
                                        none_titel = 0
                                        if bibliography_path.endswith(".bib"):
                                            for citation in citations_list:
                                                titel, author, abstract = self.find_titel_for_citation_bib(citation,
                                                                                                           bib_data)
                                                if titel is not None:
                                                    titel = self.clean_titel(titel)
                                                if titel is None:
                                                    none_titel = none_titel + 1
                                                    break
                                                citation_titel_list.append(titel)
                                                citation_author_list.append(author)
                                                citation_abstract_list.append(abstract)
                                        elif bibliography_path.endswith(".bbl"):
                                            if include_bbl is True:
                                                for citation in citations_list:
                                                    bibitem = self.find_bibitem_for_citation_bbl(citation,
                                                                                                 bibliography_path)
                                                    try:
                                                        # author, titel = "", ""
                                                        author, titel = BibitemParser.convert_single_bib_item_string_2_author_title_tuple(
                                                            self.bibitem_parser, bibitem)
                                                    except TypeError:
                                                        author, titel = "", ""
                                                    if len(titel) < 10:
                                                        none_titel += 1
                                                    citation_titel_list.append(titel)
                                                    citation_author_list.append(author)
                                        if len(citation_titel_list) > none_titel:
                                            sentence_dataset.append(
                                                {'Foldername': paper_folder_path, 'sentenceID': sentence_ID,
                                                 'sentence': clean_sentences[count],
                                                 'citations': citations_list, 'citation_titles': citation_titel_list,
                                                 'citation_authors': citation_author_list,
                                                 'citation_abstract': citation_abstract_list,
                                                 'PaperID': paper_ID, 'ParagraphID': paragraph_ID,
                                                 'Bibliography used': bibliography_path})
                        except UnicodeDecodeError:
                            sys.stderr.write("Error message: Contains none unicode characters.\n")
                except FileNotFoundError:
                    sys.stderr.write("Error message: File does not exist.\n")
                except PermissionError:
                    sys.stderr.write("Error message: Access denied.\n")
                except IsADirectoryError:
                    sys.stderr.write("Error message: Is a directory. \n")
        file_exists = os.path.isfile(output_file)
        with open(output_file, 'a', newline='', encoding='utf8') as f:
            writer = csv.DictWriter(f,
                                    fieldnames=["Foldername", "sentenceID", "sentence", "citations", "citation_titles",
                                                "citation_authors", "citation_abstract", "PaperID", "ParagraphID",
                                                "Bibliography used"])
            if not file_exists:
                writer.writeheader()
            for row in sentence_dataset:
                writer.writerow(row)
