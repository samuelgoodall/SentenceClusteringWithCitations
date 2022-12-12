from tar_extractor import TarExtractor
import unittest
import os

class TarExtractorTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tar_extractor_with_extract_folder = TarExtractor("content", "extract")
        self.tar_extractor_without_extract_folder = TarExtractor("content", "")

