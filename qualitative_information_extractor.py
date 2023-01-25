import os
import re
import uuid

import pybtex.errors
from pybtex.database.input import bibtex

from texparser.information_extractor import InformationExtractor
from texparser.SentenceListGenerator import SentenceListGenerator


class qualitativeInformationExtractor(InformationExtractor):
    
    _cite_symbols = ["\cite{", "\citet{", "\citep{", "\citet*{", "\citep*{", "\citeauthor{", "\citeyear{"]

    sentence_dataset = []
    
    def get_related_work_beginning(self, complete_file_string: str) -> int:
        related_work_symbol_position = -1
        for related_work_symbol in self._related_work_symbols:
            related_work_symbol_position = complete_file_string.find(related_work_symbol)
            if related_work_symbol_position != -1:
                break
        return related_work_symbol_position
    
                
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
        blank_line_regex = r"(?:\r?\n){2,}(?=(?:[^'\"]|'[^']*'|\"[^\"]*\")*$)" 
        return re.split(blank_line_regex, s.strip())
    
    def get_paragraphs(self, related_work:str) -> list:
        subsection_regex = r"\\(?:subsection|subsubsection|paragraph|subparagraph|newline|\\)(?:{(?:\S+(?:\S+,\s?\S+)*)})*"
        related_work = re.sub(subsection_regex, "\n\n", related_work)
        return self.split_on_empty_lines(related_work)
    
    def get_sentences(self, paragraph: str) -> list:
        sentence_list = SentenceListGenerator()
        return SentenceListGenerator.process(sentence_list, paragraph)
        
    def delete_without_citations(self, sentence_list: list) -> list:
        clean_sentence_list = []
        for sentence in sentence_list:
            cite_symbol_position = sentence[0].find(self._cite_symbol)
            if cite_symbol_position != -1:
                clean_sentence_list.append(sentence)     
        return clean_sentence_list                     
    
    def get_citation_keywords(self, sentence: str):
        citation_regex = r"\\cite(?:author|year|t|p|t\*|p\*|)(?:\[.*\])*{(\S+(?:\S+,\s?\S+)*)}"
        citation_list = re.findall(citation_regex, sentence) 
        citation_token = "<citation>"
        sentence = re.sub(citation_regex, citation_token, sentence)
        for citation in citation_list:
            if citation.find(",") != -1:
                multiple_citations = [clean_citation.strip() for clean_citation in citation.split(",")]
                for single_citation in multiple_citations:
                    citation_list.append(single_citation)
                citation_list.remove(citation)
        return citation_list
    #necessary to remove duplicates?
    
    def make_bibliography_string(self, absolute_paper_path: str, complete_file_string: str) -> str:
        file_endings = ['.bib', '.bbl']
        bib_file_found = False
        bibliography = complete_file_string
        for file_name in os.listdir(absolute_paper_path):
            if file_name.endswith(file_endings[0]):
                with open(os.path.join(absolute_paper_path, file_name), 'r') as f:
                    bibliography = f.read()
                bib_file_found = True
                break
        if not bib_file_found:
            for file_name in os.listdir(absolute_paper_path):
                if file_name.endswith(file_endings[1]):
                    with open(os.path.join(absolute_paper_path, file_name), 'r') as f:
                        bibliography = f.read()
                    break
        return bibliography
            
    
    def merge_citation_keyword_titel(self, citation_keyword:str, bibliography:str):
        position_citation = bibliography.find(citation_keyword)
        position_title = bibliography.find("titel = ")
        pass
    
    def find_titel_for_citation_bib(self, citation_keyword: str, bib_file: str):
        parser = bibtex.Parser()
        pybtex.errors.set_strict_mode(False)
        bib_data = parser.parse_file(bib_file)
        bib_data.entries.keys()
        titel = bib_data.entries[citation_keyword].fields['title']
        return titel
    
    def fill_data_set(self, absolute_paper_path: str):
        for file_name in os.listdir(absolute_paper_path):
            if file_name.endswith(".tex"):
                absolute_file_path = absolute_paper_path + "/" + file_name
                with open(absolute_file_path, 'r') as file:
                    complete_file_string = file.read()
                    paper_ID = uuid.uuid3(uuid.NAMESPACE_DNS, complete_file_string)
                    related_work_string = self.get_related_work(complete_file_string)
                    paragraphs = self.get_paragraphs(related_work_string)
                    for paragraph in paragraphs:
                        paragraph_ID = uuid.uuid3(uuid.NAMESPACE_DNS, paragraph)
                        sentences = self.get_sentences(paragraph)
                        clean_sentences = self.delete_without_citations(sentences)
                        for sentence in clean_sentences:
                            sentence_ID = uuid.uuid3(uuid.NAMESPACE_DNS, sentence[0])
                            citations_list = self.get_citation_keywords(sentence[0])
                            self.sentence_dataset.append({'sentenceID': sentence_ID, 'sentence': sentence, 'citations': citations_list, 'PaperID': paper_ID, 'ParagraphID': paragraph_ID})
        return self.sentence_dataset
   
# if __name__ == "__main__":
#     extractor = qualitativeInformationExtractor()
#     extractor.fill_data_set("texparser/")
    
#     #make clean