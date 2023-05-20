import sqlite3
from dataclasses import dataclass

from torch.utils.data import Dataset

from dataset.database.database import SQAlchemyDatabase, Paper


@dataclass
class CitationItemTO:
    citation_title: str
    citation_abstract: str


@dataclass
class DataItemTO:
    paragraph_id: int
    sentence: str
    citations: list[CitationItemTO]


class ArxivDataset(Dataset):
    """
    Map Style Dataset for our use case
    ...

    Attributes
    ----------
    db_path : str
        path to the sqlite database-file that is basis of the dataset
    length : int
        the length of the dataset
    """

    def __init__(self, db_path: str):
        """
        Parameters
        ----------
        db_path : str
            The Path to the dataset that is saved as a sqlite db
        """
        self.db_path = db_path
        database = SQAlchemyDatabase(db_path)
        session = database.session()
        engine = database.engine
        self.length = session.query(Paper).count()
        session.close()
        engine.dispose()

    def __len__(self):
        """
        Gets the length of the dataset

        Returns
        -------
        int
            The length of the dataset
        """
        return self.length

    def __getitem__(self, idx):
        """
        Gets a single Item from the Dataset

        Parameters
        ----------
        idx : int
            The index of the current item to get

        Returns
        -------
        tuple[list]
            two list first one contains the sentences
            the second one the labels belonging to the sentences(the paragraph ids)
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        sql_script = """
                        Select paragraph.id, sentence.content,c.title,c.abstract, sentence.id
                                from paragraph
                                    INNER JOIN sentence 
                                        ON sentence.paragraph_id = paragraph.id
                                        AND paper_id = ?
                                        INNER JOIN sentence_citation_relation ON
                                            sentence.id = sentence_citation_relation.sentence_id
                                                INNER JOIN citation c on c.id = sentence_citation_relation.citation_id
        """
        cursor.execute(sql_script, (idx + 1,))
        rows = cursor.fetchall()

        sentences = dict()

        for item in rows:
            sentence_id = item[4]
            paragraph_id = item[0]
            if sentence_id not in sentences:
                sentence = item[1]
                sentences[sentence_id] = DataItemTO(paragraph_id=paragraph_id, sentence=sentence, citations=list())
            sentences[sentence_id].citations.append(
                CitationItemTO(citation_title=item[2], citation_abstract=item[3] if (item[3] is not None) else ""))

        sentences = list(sentences.values())
        labels = list(map(lambda dataItem: dataItem.paragraph_id, sentences))
        return sentences, labels
