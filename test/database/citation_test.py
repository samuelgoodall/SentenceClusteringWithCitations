import os
import sys
import unittest

sys.path.append(".")
from database.base import session_factory,engine
from database.citation import Citation

from database_test import DatabaseTest

class CitationTest(DatabaseTest):
        
    def test_citation_saving(self) -> None:
        saved_citation = Citation("title", "author")
        self.session.add(saved_citation)
        self.session.commit()
        loaded_citation = self.session.query(Citation).first()
        self.assertEqual(loaded_citation, saved_citation, "citation not saved in database")
        
if __name__ == "__main__":  
    unittest.main()