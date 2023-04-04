import pickle
import sqlite3
import time

from numpy._typing import ArrayLike
from torch.utils.data import DataLoader

from dataset.customDataloader import ArxivDataset, custom_collate, get_dataloader
from dataclasses import dataclass


@dataclass
class CitationItemTO:
    citation_title: str
    citation_title_embedded: str
    citation_abstract: str


@dataclass
class DataItemTO:
    paragraph_id: int
    sentence: str
    sentence_embedded: ArrayLike
    citations: list[CitationItemTO]


class ArxivDatasetPrecomputedEmbeddings(ArxivDataset):
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
                        Select paragraph.id, sentence.content,sentence.content_embedded,c.title,c.title_embedded,c.abstract, sentence.id
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
            sentence_id = item[6]
            paragraph_id = item[0]
            if sentence_id not in sentences:
                sentence = item[1]
                sentence_embedded = pickle.loads(item[2])
                sentences[sentence_id] = DataItemTO(paragraph_id=paragraph_id,
                                                    sentence=sentence,
                                                    sentence_embedded=sentence_embedded,
                                                    citations=list())
            citation_embedded = pickle.loads(item[4])
            sentences[sentence_id].citations.append(CitationItemTO(citation_title=item[3],
                                                                   citation_title_embedded=citation_embedded,
                                                                   citation_abstract=item[5] if (item[5] is not None) else ""))

        sentences = list(sentences.values())
        labels = list(map(lambda dataItem: dataItem.paragraph_id, sentences))
        return sentences, labels


if __name__ == "__main__":
    """
    just used for manual testing
    """
    dataset = ArxivDatasetPrecomputedEmbeddings("../dataset/database/dataset_new_precomputed_embeddings_sbert.db")
    train_dataloader = DataLoader(dataset, batch_size=200, shuffle=False, collate_fn=custom_collate)
    train_dataloader = get_dataloader(batch_size=200, shuffle=False,
                                      dataset_location="../dataset/database/dataset_new_precomputed_embeddings_bert.db")
    start = time.time()
    example = next(iter(train_dataloader))
    end = time.time()

    print("seconds", end - start)
