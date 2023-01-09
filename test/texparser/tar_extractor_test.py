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
        example_file = "arXiv_src_1705_016.tar"
        self.tar_extractor_without_extract_folder._create_file_folder_path(example_file, ".tar")
        filenames = os.listdir(self.tar_extractor_without_extract_folder.dataset_folder_path)
        self.assertIn(example_file.replace(".tar", ""), filenames)

    def test_create_file_folder_path_with_extract_folder(self):
        example_file = "arXiv_src_1705_016.tar"
        example_folder = "filename"
        self.tar_extractor_with_extract_folder.create_extract_folder_path()
        self.tar_extractor_with_extract_folder._create_file_folder_path(example_file, ".tar")
        path_to_folder = os.path.join(self.tar_extractor_with_extract_folder.extract_folder_path, self.tar_extractor_with_extract_folder.dataset_folder_path)
        filenames = os.listdir(path_to_folder)
        self.assertIn(example_folder, filenames)

    def test_extract_file_into_folder(self):
        example_file = "filename.tar"
        example_folder = example_file.replace(".tar", "")
        self.tar_extractor_with_extract_folder.create_extract_folder_path()
        #t = TarExtractor("content", "extract")
        self.tar_extractor_with_extract_folder._extract_file_into_folder(example_file, "filler", ".tar")
        path_to_folder = os.path.join(self.tar_extractor_with_extract_folder.extract_folder_path, self.tar_extractor_with_extract_folder.dataset_folder_path)
        filenames = os.listdir(path_to_folder)
        self.assertIn(example_folder, filenames)

    def tearDown(self) -> None:
        if os.path.exists(self.tar_extractor_with_extract_folder.extract_folder_path):
            shutil.rmtree(self.tar_extractor_with_extract_folder.extract_folder_path, ignore_errors=True)
        if os.path.exists(self.tar_extractor_with_extract_folder.dataset_folder_path):
            shutil.rmtree(self.tar_extractor_with_extract_folder.dataset_folder_path, ignore_errors=True)
            os.rename("content_backup", "content")

if __name__ == "__main__":
    unittest.main()
