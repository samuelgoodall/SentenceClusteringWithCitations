import ast
import csv
import json

from database.database import (Citation, Paragraph, Sentence, engine,
                               session_factory)


def feed_database():
    session = session_factory()
    
    filename = open("output/data2.csv", "r", encoding = "utf8")
    file = csv.DictReader(filename)
    for col in file:
        sentence = (col['sentence'])
        saved_sentence = Sentence(sentence)
        session.add(saved_sentence)
        session.commit()
        titels = (col['citation_titles'])
        authors = (col['citation_authors'])
        titel_list = ast.literal_eval(titels)
        for titel in titel_list:
            saved_citation = Citation(titel, authors)
            session.add(saved_citation)
            session.commit()
            saved_sentence.citations.append(saved_citation)
            session.add(saved_sentence)
            session.commit()
        paragraph_id = (col['ParagraphID'])
        saved_paragraph = Paragraph()
        session.add(saved_paragraph)
        session.commit()
        saved_sentence.paragraph = Paragraph()
        session.add(saved_sentence)
        session.commit()
    
feed_database()