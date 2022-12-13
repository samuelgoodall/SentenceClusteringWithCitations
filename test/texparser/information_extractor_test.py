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

    def test_length_related_work_no_string(self):
        related_work_length = self.information_extractor._InformationExtractor__length_related_work("", 5503)
        self.assertEqual(-1, related_work_length)

    def test_length_related_work_no_related_work(self):
        test_string = self.boiler_plate + self.next_section_symbol
        related_work_length = self.information_extractor._InformationExtractor__length_related_work(test_string, -1)
        self.assertEqual(-1, related_work_length)

    def test_length_related_work_no_following_section(self):
        test_string = self.related_work_symbol + self.boiler_plate
        related_work_length = self.information_extractor._InformationExtractor__length_related_work(test_string, 0)
        self.assertEqual(len(test_string) - 3, related_work_length)

    def test_length_related_work_with_proper_related_work(self):
        test_string = self.related_work_symbol + self.boiler_plate +self.next_section_symbol
        related_work_length = self.information_extractor._InformationExtractor__length_related_work(test_string, 0)
        real_related_work_length = len(self.boiler_plate)
        self.assertEqual(real_related_work_length, related_work_length)

if __name__ == "__main__":  
    unittest.main()
