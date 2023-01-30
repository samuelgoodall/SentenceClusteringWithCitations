import csv
import os
import re
import sys
import uuid

import pybtex.errors
from pybtex.database.input import bibtex

from bibitem_parsing.bibitem_parser import BibitemParser
from texparser.information_extractor import InformationExtractor
from texparser.SentenceListGenerator import SentenceListGenerator


class QualitativeInformationExtractor(InformationExtractor):
    
    def __init__(self):
        super().__init__()
        self.bibitem_parser = BibitemParser()

    _cite_symbols = ["\cite{", "\citet{", "\citep{", "\citet*{", "\citep*{", "\citeauthor{", "\citeyear{"]

    
    def get_related_work_beginning(self, complete_file_string: str) -> int:
        related_work_symbol_position = -1
        length = 0
        for related_work_symbol in self._related_work_symbols:
            related_work_symbol_position = complete_file_string.find(related_work_symbol)
            if related_work_symbol_position != -1:
                length = len(related_work_symbol)
                break
        return related_work_symbol_position + length
    
                
    def get_related_work_end(self, complete_file_string:str) -> int:
        related_work_symbol_position = self.get_related_work_beginning(complete_file_string)
        related_work_length = self.length_related_work(complete_file_string, related_work_symbol_position)
        if related_work_length == -1:
            return -1
        else:
            return related_work_symbol_position + related_work_length
                    
    def get_related_work(self, complete_file_string:str) -> str:
        related_work = complete_file_string[self.get_related_work_beginning(complete_file_string):self.get_related_work_end(complete_file_string)]
        return related_work
    
    def split_on_empty_lines(self, s: str) -> list:
        # greedily match 2 or more new-lines, but not inside quote
        blank_line_regex = r"(?:\r?\n){2,}(?=(?:[^\"]|\"[^\"]*\")*$)" 
        return re.split(blank_line_regex, s.strip())
    
    def get_paragraphs(self, related_work:str) -> list:
        subsection_regex = r"\\(?:subsection|subsubsection|paragraph|subparagraph|newline|\\|break|linebreak)(?:{.*?})*|(?:\[.*?\])"
        related_work = re.sub(subsection_regex, "\n\n", related_work)
        return self.split_on_empty_lines(related_work)
    
    def find_citations_paragraph_end(self, paragraph: str):
        citation_paragraph_end_regex = r"~?(?:\\cite(?:author|year|t|p|t\*|p\*|)(?:\[.*\])*{.*?})$"
        citation_paragraph_end = re.search(citation_paragraph_end_regex, paragraph) 
        return citation_paragraph_end
    
    def delete_citation_paragraph_end(self, paragraph:str, citation_paragraph_end):
        citation_paragraph_end_regex = r"~?(?:\\cite(?:author|year|t|p|t\*|p\*|)(?:\[.*\])*{.*?})$"
        if citation_paragraph_end is not None:
            paragraph = re.sub(citation_paragraph_end_regex, "", paragraph)
        return paragraph   
     
    def get_sentences(self, paragraph: str) -> list:
        sentence_list = SentenceListGenerator()
        return SentenceListGenerator.process(sentence_list, paragraph)
    
    def put_citation_paragraph_end_in_sentence(self, sentence, citation_end_paragraph):
        if citation_end_paragraph is not None and sentence != "":
            sentence = sentence + citation_end_paragraph.group()
        return sentence
    
    def delete_without_citations(self, sentence_list: list) -> list:
        clean_sentence_list = []
        for sentence in sentence_list:
            cite_symbol_position = sentence.find(self._cite_symbol)
            if cite_symbol_position != -1:
                clean_sentence_list.append(sentence)     
        return clean_sentence_list                     
    
    def clean_sentence(self, sentence:str):
        command_regex = re.compile(r"\\(?!cite).*?(?:\[.*?\])?(?:(?:{.*?})|\s)")
        text_in_command_as_group_regex = re.compile(r"\\(?!cite).*?(?:\[.*?\])?(?:(?:{(.*?)})|\s)")
        command_list = re.findall(command_regex, sentence)
        text_list = re.findall(text_in_command_as_group_regex, sentence)
        for count, command in enumerate(command_list):
            if (text_list[count] != "itemize"):
                sentence = sentence.replace(command, text_list[count])
            else:
                sentence = sentence.replace(command, "")
        sentence = re.sub(r"(?<!\\)\$.*?\$", "", sentence)
        return sentence
    
    def get_citation_keywords(self, sentence):
        citation_regex = r"~?\\cite(?:author|year|t|p|t\*|p\*|)(?:\[.*\])*{(\S+(?:\S+,\s?\S+)*)}"
        citation_list = re.findall(citation_regex, sentence)
        for citation in citation_list:
            if citation.find(",") != -1:
                multiple_citations = [clean_citation.strip() for clean_citation in citation.split(",")]
                for single_citation in multiple_citations:
                    citation_list.append(single_citation)
                citation_list.remove(citation)
        return citation_list
    
    def check_bibliography_type(self, paper_folder_path: str) -> str:
        file_endings = ['.bib', '.bbl']
        bib_file_found = False
        bibliography_path = ""
        for file_name in os.listdir(str(paper_folder_path)):
            if file_name.endswith(file_endings[0]):
                bibliography_path = os.path.join(paper_folder_path, file_name)
                bib_file_found = True
                break
        if not bib_file_found:
            for file_name in os.listdir(str(paper_folder_path)):
                if file_name.endswith(file_endings[1]):
                    bibliography_path = os.path.join(paper_folder_path, file_name)
                    break
        return bibliography_path
    
    def find_titel_for_citation_bib(self, citation_keyword: str, bib_file: str):
        parser = bibtex.Parser()
        pybtex.errors.set_strict_mode(False)
        try:
            bib_data = parser.parse_file(bib_file)
            bib_data.entries.keys()
            try:
                titel = bib_data.entries[citation_keyword].fields['title']
            except KeyError:
                titel = None
            try:
                author = bib_data.entries[citation_keyword].fields['author']
            except KeyError:
                author = None
        except UnicodeDecodeError:
            titel = None
            author = None
        except:
            titel = None
            author = None
        return titel, author
    
    def find_bibitem_for_citation_bbl(self, citation_keyword: str, bib_file: str):
        #find citation keyword and return string until line break with empty line
        blank_line_regex = r"(?:\r?\n){2,}" 
        with open(os.path.join(bib_file), 'r') as f:
            bibliography = f.read()
        bibitem_key = "\\bibitem{" + citation_keyword + "}"
        start_bibitem  = bibliography.find(bibitem_key)
        sliced_bibliography = bibliography[start_bibitem:]
        match = re.search(blank_line_regex, sliced_bibliography)
        end_bibitem = len(sliced_bibliography) 
        if match:
            end_bibitem = match.start()    
        #bibitem = re.search(rf"\{bibitem_key}.*?(?:\n\n.*?\\)|$", bibliography, re.DOTALL)
        bibitem = sliced_bibliography[:end_bibitem]
        return bibitem
    
    def fill_data_set(self, paper_folder_path: str, output_file: str):
        sentence_dataset = []
        for file_name in os.listdir(str(paper_folder_path)):
            if file_name.endswith(".tex"):
                absolute_paper_path = os.path.join(paper_folder_path, file_name)
                try:
                    with open(absolute_paper_path, 'r', encoding="utf-8") as file:
                        try:
                            complete_file_string = file.read()
                            paper_ID = uuid.uuid3(uuid.NAMESPACE_DNS, complete_file_string).urn
                            if self.get_related_work_beginning(complete_file_string) != -1:
                                related_work_string = self.get_related_work(complete_file_string)
                                paragraphs = self.get_paragraphs(related_work_string)
                                for index, paragraph in enumerate(paragraphs):
                                    paragraph_ID = uuid.uuid3(uuid.NAMESPACE_DNS, paragraph).urn
                                    citation_paragraph_end = self.find_citations_paragraph_end(paragraph)
                                    paragraphs[index] = self.delete_citation_paragraph_end(paragraph, citation_paragraph_end)
                                    sentences = self.get_sentences(paragraphs[index])
                                    for index, sentence in enumerate(sentences):
                                        sentences[index] = self.put_citation_paragraph_end_in_sentence(sentence, citation_paragraph_end)
                                    clean_sentences = self.delete_without_citations(sentences)
                                    for count, sentence in enumerate(clean_sentences):
                                        sentence_ID = uuid.uuid3(uuid.NAMESPACE_DNS, sentence).urn
                                        citations_list = self.get_citation_keywords(sentence)
                                        clean_sentences[count] = self.clean_sentence(sentence)
                                        citation_titel_list = []
                                        citation_author_list = []
                                        none_titel = 0
                                        bibliography_path = self.check_bibliography_type(paper_folder_path)
                                        if bibliography_path.endswith(".bib"):
                                            for citation in citations_list:
                                                titel, author = self.find_titel_for_citation_bib(citation, bibliography_path)
                                                if titel is None:
                                                    none_titel = none_titel + 1
                                                    break
                                                citation_titel_list.append(titel)
                                                citation_author_list.append(author)
                                        elif bibliography_path.endswith(".bbl"):
                                            for citation in citations_list:
                                                bibitem = self.find_bibitem_for_citation_bbl(citation, bibliography_path)
                                                # author, titel = BibitemParser.convert_single_bib_item_string_2_author_title_tuple(self.bibitem_parser, bibitem)
                                                titel = bibitem
                                                citation_titel_list.append(titel)
                                                #citation_author_list.append(author)
                                        if len(citations_list) > none_titel:
                                            sentence_dataset.append({'sentenceID': sentence_ID, 'sentence': clean_sentences[count], 'citations': citations_list, 'citation_titles': citation_titel_list, 'citation_authors': citation_author_list, 'PaperID': paper_ID, 'ParagraphID': paragraph_ID})            
                            file_exists = os.path.isfile(output_file)
                            with open(output_file, 'a', newline='') as f:
                                writer = csv.DictWriter(f, fieldnames=["sentenceID", "sentence", "citations", "citation_titles", "citation_authors", "PaperID", "ParagraphID"])
                                if not file_exists:
                                    writer.writeheader()
                                for row in sentence_dataset:
                                    writer.writerow(row)
                        except UnicodeDecodeError:
                            sys.stderr.write("Error message: Contains none unicode characters.\n")           
                except FileNotFoundError:
                    sys.stderr.write("Error message: File does not exist.\n")
                except PermissionError:
                    sys.stderr.write("Error message: Access denied.\n")
                except IsADirectoryError:
                    sys.stderr.write("Error message: Is a directory. \n")