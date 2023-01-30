import os
import sys
import unittest

sys.path.append(".")
from database.database import Citation, Sentence, engine, session_factory


class DatabaseTest(unittest.TestCase):
    def setUp(self) -> None: 
        self. session = session_factory()
        
    def test_citation_saving(self) -> None:
        saved_citation = Citation("title", "author")
        self.session.add(saved_citation)
        self.session.commit()
        loaded_citation = self.session.query(Citation).first()
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
        
    def tearDown(self) -> None:
        engine.dispose()
        os.remove("student.db")
        
if __name__ == "__main__":
    unittest.main()