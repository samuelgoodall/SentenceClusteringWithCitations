from tar_extractor import TarExtractor
import unittest
import os

class TarExtractorTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tar_extractor_with_extract_folder = TarExtractor("content", "extract")
        self.tar_extractor_without_extract_folder = TarExtractor("content", "")

    def test_create_extract_folder_path(self):
        self.tar_extractor_with_extract_folder.create_extract_folder_path()
        filenames = os.listdir(".")
        self.assertIn("extract", filenames)

    def test_create_extract_empty_folder_path(self):
        old_filenames = os.listdir(".")
        self.tar_extractor_without_extract_folder.create_extract_folder_path()
        filenames = os.listdir(".")
        self.assertEqual(old_filenames, filenames)
