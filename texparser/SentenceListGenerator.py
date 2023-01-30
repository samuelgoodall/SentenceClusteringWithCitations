import logging
import re


class SentenceListGenerator:
    """  Split into sentences based on the regex.

    Returns a list of tuples ("sentence", start_pos)

    Tries to construct a complex regex based on a list of abbreviations to ignore most abbreviations.

    If that fails, a more simple regex is used. The simple regex has a greater chance of matching to the
    wrong characters. (For example to split the sentence at an abbreviations instead of the sentence end.

    Regex based on  https://stackoverflow.com/a/25736082
    Improved by using the list of abbreviations in ./SentenceListAbbreviations.txt
    """
    __slots__ = ["_sentence_split_regex_", "_comment_regex_"]

    def __init__(self):
        """ Initiates a SentenceListGenerator.

        Creates a new regex based on the abbreviations list. Uses simpler regex if this fails.
        """
        #self._comment_regex_ = re.compile(r"^(.*[^\\])?%.*")  # used to filter comments
        self._comment_regex_ = re.compile(r"(?<!\\)%.*")
        try:
            with open("texparser/SentenceListAbbreviations.txt") as abbrev:
                abbreviations = abbrev.read()

            abbreviations = abbreviations.replace(".", '\.').splitlines(keepends=False)
            abbrev_regex = ")(?<!\s".join(abbreviations)
            quote_regex = "(?=(?:[^'\"]|'[^']*'|\"[^\"]*\")*$)" #add to not split sentences inside quotes
            self._sentence_split_regex_ = re.compile(fr"(?<!\w\.\w.)(?<!\s{abbrev_regex})(?<![A-Z][a-z]\.)(?<=[.?!])\s{quote_regex}")
            
            logging.info(f"{self.get_name()}: Successfully created regex {self._sentence_split_regex_}")
            

        except (IOError, FileNotFoundError, PermissionError) as e:
            logging.error(f"{self.get_name()}: Reading Abbreviations failed! Falling back to simplified version.\n{e}")
            self._sentence_split_regex_ = re.compile(r"(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=[.?!])\s")
        except re.error as e:
            logging.error(f"{self.get_name()}: Compling regex failed! Falling back to simplified version.\n{e}")
            self._sentence_split_regex_ = re.compile(r"(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=[.?!])\s")

    def process(self, text_content: str) -> list:
        """ Splits the LaTeX string of the given Task into sentences.

        :param task: the Task to process.
        :type task: Task
        :return: list of sentences.
        :rtype: list[str]
        """
        # TODO: Fix wrong offsets
        #text = task.latex_text
        #text_content = str(task.latex_soup.document)

        # to remove comments:
        for matches in self._comment_regex_.findall(text_content):
            for match in matches:
                text_content = text_content.replace(match[0], "")

        text_content = re.sub(r"\s", " ", text_content)

        parsed = re.split(self._sentence_split_regex_, text_content)

        return list(parsed)

    def get_name(self) -> str:
        return "Sentence List Generator"