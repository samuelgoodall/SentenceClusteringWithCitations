import os
import sys
import unittest

sys.path.append(".")
from database.database import (Citation, Paragraph, Sentence, SQAlchemyDatabase)


class DatabaseTest(unittest.TestCase):
    def setUp(self) -> None:
        abs_path = os.path.abspath("dataset.db")
        print("abs_path", abs_path)
        self.session = SQAlchemyDatabase(abs_path).session()
        self.engine = SQAlchemyDatabase(abs_path).engine

    def test_citation_saving(self) -> None:
        saved_citation = Citation("title", "author")
        self.session.add(saved_citation)
        self.session.commit()
        loaded_citation = self.session.query(Citation).first()
        print("loaded_citation", loaded_citation.title)
        self.assertEqual(loaded_citation, saved_citation, "citation not saved in database")

    def test_sentence_saving(self) -> None:
        saved_sentence = Sentence("Sentence")
        self.session.add(saved_sentence)
        self.session.commit()
        loaded_citation = self.session.query(Sentence).first()
        self.assertEqual(loaded_citation, saved_sentence, "sentences not saved in database")
        
    def test_sentence_citation_relation(self) -> None:
        saved_sentence = Sentence("Sentence")
        saved_sentence.citations.append(Citation("title", "author"))
        self.session.add(saved_sentence)
        self.session.commit()
        loaded_sentence = self.session.query(Sentence).first()
        self.assertEqual(loaded_sentence, saved_sentence, "sentence citation relation not saved in database")
        
    def test_paragraph_saving(self) -> None:
        saved_paragraph = Paragraph()
        self.session.add(saved_paragraph)
        self.session.commit()
        loaded_paragraph = self.session.query(Paragraph).first()
        self.assertEqual(loaded_paragraph, saved_paragraph, "Paragraph not saved in database")
        
    def test_sentence_paragraph_relation(self) -> None:
        saved_sentence = Sentence("Sentence")
        saved_sentence.paragraph = Paragraph()
        self.session.add(saved_sentence)
        self.session.commit()
        loaded_sentence = self.session.query(Sentence).first()
        self.assertEqual(loaded_sentence, saved_sentence, "sentence paragraph relation not saved in database")

    def tearDown(self) -> None:
        self.engine.dispose()

        abs_path = os.path.abspath("dataset.db")
        print("TearDown abs_path", abs_path)
        os.remove(abs_path)
        
if __name__ == "__main__":
    unittest.main()
