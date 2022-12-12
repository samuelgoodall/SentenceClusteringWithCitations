import unittest
import sys
sys.path.append(".")
from texparser.information_extractor import InformationExtractor

class InformationExtractorTest(unittest.TestCase):
    def setUp(self) -> None:
        self.information_extractor = InformationExtractor()
        self.related_work_symbol = "\section{Related Work}"
        self.boiler_plate = "sdfsjfdkjs djfhskj dhfksh"
        self.next_section_symbol = "\section{Next Section}"
