import os
import sys
import unittest

sys.path.append(".")
from database.base import session_factory,engine
from database.sentence import Sentence

from database_test import DatabaseTest

class CitationTest(DatabaseTest):
        
    def test_sentence_saving(self) -> None:
        saved_sentence = Sentence("Sentence")
        self.session.add(saved_sentence)
        self.session.commit()
        loaded_citation = self.session.query(Sentence).first()
        self.assertEqual(loaded_citation, saved_sentence, "sentences not saved in database")
        
if __name__ == "__main__":  
    unittest.main()