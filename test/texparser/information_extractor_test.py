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

    def test_get_length_related_work_no_string(self):
        related_work_length = self.information_extractor._InformationExtractor__get_length_related_work("", 5503)
        self.assertEqual(-1, related_work_length)
