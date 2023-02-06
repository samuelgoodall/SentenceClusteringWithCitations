import os
import shutil
import sys
import unittest

sys.path.append(".")
from texparser.tar_extractor import TarExtractor


class TarExtractorTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tar_extractor_with_extract_folder = TarExtractor("content", "extract")
        self.tar_extractor_without_extract_folder = TarExtractor("content", "")
        shutil.copytree("content", "content_backup")

    def test_create_extract_folder_path(self):
        self.tar_extractor_with_extract_folder.create_extract_folder_path()
        filenames = os.listdir(".")
        self.assertIn("extract", filenames)

    def test_create_extract_empty_folder_path(self):
        old_filenames = os.listdir(".")
        self.tar_extractor_without_extract_folder.create_extract_folder_path()
        filenames = os.listdir(".")
        self.assertEqual(old_filenames, filenames) 

    def test_create_file_folder_path_with_empty_extract_folder(self):
        example_file = "arXiv_src_1505_016.tar"
        self.tar_extractor_without_extract_folder._create_file_folder_path(example_file, ".tar")
        filenames = os.listdir(self.tar_extractor_without_extract_folder.dataset_folder_path)
        self.assertIn(example_file, filenames)

    def tearDown(self) -> None:
        if os.path.exists(self.tar_extractor_with_extract_folder.extract_folder_path):
            shutil.rmtree(self.tar_extractor_with_extract_folder.extract_folder_path, ignore_errors=True)
        if os.path.exists(self.tar_extractor_with_extract_folder.dataset_folder_path):
            shutil.rmtree(self.tar_extractor_with_extract_folder.dataset_folder_path, ignore_errors=True)
            os.rename("content_backup", "content")

if __name__ == "__main__":
    unittest.main()
