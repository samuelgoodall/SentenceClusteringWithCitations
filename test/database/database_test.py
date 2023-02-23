import os
import sys
import unittest

sys.path.append(".")
from database.database import (Citation, Paragraph, Sentence, SQAlchemyDatabase, Paper)


class DatabaseTest(unittest.TestCase):
    def setUp(self) -> None:
        abs_path = os.path.abspath("dataset.db")
        print("abs_path", abs_path)
        self.session = SQAlchemyDatabase(abs_path).session()
        self.engine = SQAlchemyDatabase(abs_path).engine

    def test_citation_saving(self) -> None:
        saved_citation = Citation(title="title", author="author")
        self.session.add(saved_citation)
        self.session.commit()
        loaded_citation = self.session.query(Citation).first()
        print("loaded_citation", loaded_citation.title)
        self.assertEqual(loaded_citation, saved_citation, "citation not saved in database")

    def test_sentence_saving(self) -> None:
        saved_sentence = Sentence(content="Sentence")
        self.session.add(saved_sentence)
        self.session.commit()
        loaded_citation = self.session.query(Sentence).first()
        self.assertEqual(loaded_citation, saved_sentence, "sentences not saved in database")

    def test_sentence_citation_relation(self) -> None:
        saved_sentence = Sentence(content="Sentence")
        saved_sentence.citations.append(Citation(title="title", author="author"))
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
        saved_sentence = Sentence(content="Sentence")
        saved_sentence.paragraph = Paragraph()
        self.session.add(saved_sentence)
        self.session.commit()
        loaded_sentence = self.session.query(Sentence).first()
        self.assertEqual(loaded_sentence, saved_sentence, "sentence paragraph relation not saved in database")

    def test_paper_saving(self) -> None:
        saved_paper = Paper()
        self.session.add(saved_paper)
        self.session.commit()
        loaded_paper = self.session.query(Paper).first()
        self.assertEqual(loaded_paper, saved_paper, "paper wasnt saved properly!")

    def test_paper_paragraph_relation(self):
        saved_paper = Paper(title="TITLE",authors="AUTHORS")
        saved_paragraph = Paragraph()
        saved_paragraph.paper = saved_paper
        self.session.add(saved_paper)
        loaded_paragraph = self.session.query(Paragraph).first()
        self.assertEqual(saved_paragraph,loaded_paragraph,"paper_paragraph_relation not saved in database!")

    def tearDown(self) -> None:
        self.engine.dispose()
        abs_path = os.path.abspath("dataset.db")
        print("TearDown abs_path", abs_path)
        os.remove(abs_path)


if __name__ == "__main__":
    unittest.main()
