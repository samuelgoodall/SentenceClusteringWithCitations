import unittest

from bibitem_parsing.bibitem_parser import BibitemParser


class BibitemParserTest(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(BibitemParserTest, self).__init__(*args, **kwargs)
        # TODO make it read from a configuration file
        self.bibitem_parser = BibitemParser()
        self.test_bib_item_with_newblock = "\bibitem{ahsan2019video}\nUnaiza Ahsan, Rishi Madhok, and Irfan Essa.\n\newblock {Video Jigsaw: Unsupervised Learning of Spatiotemporal Context for\n Video Action Recognition}.\n\newblock In {\em WACV}, pages 179--189. IEEE, 2019."

    def setUp(self) -> None:
        """call before every testcase"""

    def test_strip_special_chars__stringInput_cleanedString(self):
        # arrange
        test_input = "\\newblock {Video Jigsaw: Unsupervised Learning of Spatiotemporal Context for\n Video Action Recognition}"
        asserted_output = "{Video Jigsaw: Unsupervised Learning of Spatiotemporal Context for Video Action Recognition}"

        # act
        output = self.bibitem_parser._strip_special_chars(test_input)

        # assert
        self.assertEqual(output, asserted_output)

    def test_strip_special_chars__emptyStringInput_returnStringInput(self):
        # arrange
        test_input = ""
        asserted_output = ""

        # act
        output = self.bibitem_parser._strip_special_chars(test_input)

        # assert
        self.assertTrue(output == asserted_output)

    def test_strip_special_chars__stringInputAndNoSpecialChars_returnStringInput(self):
        # arrange
        testinput = "Image{N}et: {A} {L}arge-{S}cale {H}ierarchical {I}mage {D}atabase"
        assertedoutput = "Image{N}et: {A} {L}arge-{S}cale {H}ierarchical {I}mage {D}atabase"

        # act
        output = self.bibitem_parser._strip_special_chars(testinput)

        # assert
        self.assertTrue(output == assertedoutput)

    def test_strip_special_chars__nonStringInput_AssertionError(self):
        # arrange
        test_input = 5

        # act&assert
        # Todo think of edgecases other than int maybe something that might be close to a string

        with self.assertRaises(AssertionError) as context:
            self.bibitem_parser._strip_special_chars(test_input)

    def test_strip_letter_encasing__stringInput_stringWithStrippedLetterEncasings(self):
        # arrange
        test_input = "Image{N}et: {A} {L}arge-{S}cale {H}ierarchical {I}mage {D}atabase"
        asserted_output = "ImageNet: A Large-Scale Hierarchical Image Database"

        # act
        output = self.bibitem_parser._strip_letter_encasing(test_input)

        # assert
        self.assertTrue(output == asserted_output)

    def test_strip_letter_encasing__noLetterEncasingInStringInput_returnStringInput(self):
        # arrange
        test_input = "\\newblock {Video Jigsaw: Unsupervised Learning of Spatiotemporal Context for\\n Video Action Recognition}"
        asserted_output = "\\newblock {Video Jigsaw: Unsupervised Learning of Spatiotemporal Context for\\n Video Action Recognition}"

        # act
        output = self.bibitem_parser._strip_letter_encasing(test_input)

        # assert
        self.assertTrue(output == asserted_output)

    def test_strip_special_chars__noneStringInput_AssertionError(self):
        # arrange
        testinput = 5

        # act&assert
        with self.assertRaises(AssertionError) as context:
            self.bibitem_parser._strip_letter_encasing(testinput)

    def test_convert_bibtexstring_2_author_title_tuple__StringInput1_returnCorrectStringInput(self):
        # arrange
        testinput = "@book{zsllwd20,\nauthor = {Xizhou Zhu and Weijie Su and Lewei Lu and Bin Li and Xiaogang Wang and Jifeng Dai.},\ntitle = {Sequence to sequence learning with\n  neural networks,},\nyear = {2020},\naddress = {},\npublisher = {ICLR}  \end{thebibliography},}"
        asserted_output = "Sequence to sequence learning with neural networks"
        # act
        author, output = self.bibitem_parser._convert_bibtexstring_2_author_title_tuple(testinput)
        # assert
        self.assertEqual(asserted_output, output)

    def test_clean_string__noneStringInput_AssertionError(self):
        # arrange
        testinput = 5

        # act&assert
        with self.assertRaises(AssertionError) as context:
            self.bibitem_parser._clean_string(testinput)

    def test_clean_string__stringInput_cleanedString(self):
        # arrange
        test_input = "\\newblock {Video Jigsaw: Unsupervised Learning of Spatiotemporal Context for\\n Video Action Recognition}"
        asserted_output = "Video Jigsaw: Unsupervised Learning of Spatiotemporal Context for Video Action Recognition"

        # act
        output = self.bibitem_parser._clean_string(test_input)

        # assert
        message = "Output \n" + output + "\ndoesnt match asserted output\n " + asserted_output + "."
        self.assertTrue(output == asserted_output, message)

    def test_clean_string__stringInput_stringWithStrippedLetterEncasings(self):
        # arrange
        test_input = "Image{N}et: {A} {L}arge-{S}cale {H}ierarchical {I}mage {D}atabase"
        asserted_output = "ImageNet: A Large-Scale Hierarchical Image Database"

        # act
        output = self.bibitem_parser._clean_string(test_input)

        # assert
        self.assertTrue(output == asserted_output)

    def test_clean_string__emptyStringInput_returnStringInput(self):
        # arrange
        test_input = ""
        asserted_output = ""

        # act
        output = self.bibitem_parser._clean_string(test_input)

        # assert
        self.assertTrue(output == asserted_output)

    def test_clean_string__stringInputAndNoSpecialChars_returnStringInput(self):
        # arrange
        testinput = "Image{N}et: {A} {L}arge-{S}cale {H}ierarchical {I}mage {D}atabase"
        assertedoutput = "ImageNet: A Large-Scale Hierarchical Image Database"

        # act
        output = self.bibitem_parser._clean_string(testinput)

        # assert
        message = "Test input \n" + testinput + "\ndoesnt match asserted output\n " + assertedoutput + "."
        self.assertTrue(output == assertedoutput, message)


if __name__ == "__main__":
    unittest.main()  # run all tests
