import sqlite3
import time

import torch
from torch.utils.data import Dataset, DataLoader, random_split

from dataset.database.database import SQAlchemyDatabase, Paper


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
                        Select paragraph.id, sentence.content,c.title,c.abstract
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
        sentences = []
        labels = []
        for item in rows:
            sentence_citation = {
                "sentence": item[1],
                "citation_title": item[2],
                "citation_abstract": item[3] if (item[3] is not None) else "",
            }
            sentences.append(sentence_citation)
            labels.append(item[0])
        return sentences, labels


def custom_collate(batch: list):
    """
    needed because of our special structure of dataset otherwise it would try to vectorize the data which doesn´t work!

    Parameters
    ----------
    batch : list
        a list of examples dataset items

    Returns
    -------
    batch
       just the untransformed batch
    """
    return batch


def get_dataloader(batch_size: int = 20, shuffle: bool = False):
    """
    gets the dataloader on the whole dataset

    Parameters
    ----------
    batch_size : int
        The size of the batch = how many examples are fetched
    shuffle : bool
        Sets wether dataloader shall shuffle the data whilst iterating

    Returns
    -------
    DataLoader
       DataLoader for the whole Dataset
    """
    whole_dataset = ArxivDataset("../dataset/database/dataset.db")
    return DataLoader(whole_dataset, batch_size=batch_size, shuffle=shuffle, collate_fn=custom_collate)


def get_train_test_validation_dataloader(batch_size: int = 20, shuffle: bool = True,
                                         train_test_validation_split: list[float] = [], fixed_random_seed: int = None):
    """
    gets the dataloaders for train test and validation

    Parameters
    ----------
    batch_size : int
        The size of the batch = how many examples are fetched
    shuffle : bool
        Sets wether dataloader shall shuffle the data whilst iterating
    train_test_validation_split : list[float]
        The ratio of train test and validation split of the whole dataset, list of floats has to sum to 1
    fixed_random_seed : int
        seed that can be set for reproducable results

    Returns
    -------
    tuple[DataLoader]
        the train,test and validation dataloader

    Raises
    ------
    ValueError
        If no sound is set for the animal or passed in as a
        parameter.
    """

    if len(train_test_validation_split) < 3 or train_test_validation_split is None:
        raise ValueError("train_test_validation_split must be given! has to be array/list of floats that sum up to 1!")

    if sum(train_test_validation_split) != 1.0:
        raise ValueError("train_test_validation_split values have to sum up to 1!")

    whole_dataset = ArxivDataset("../dataset/database/dataset.db")
    if fixed_random_seed is None:
        train_dataset, test_dataset, validation_dataset = random_split(whole_dataset,
                                                                       train_test_validation_split)
    else:
        train_dataset, test_dataset, validation_dataset = random_split(whole_dataset,
                                                                       train_test_validation_split,
                                                                       generator=torch.Generator().manual_seed(
                                                                           fixed_random_seed))
    train_dataloader = DataLoader(train_dataset, batch_size=batch_size,
                                  shuffle=shuffle, collate_fn=custom_collate)
    test_dataloader = DataLoader(test_dataset, batch_size=batch_size,
                                 shuffle=shuffle, collate_fn=custom_collate)
    validation_dataloader = DataLoader(validation_dataset, batch_size=batch_size,
                                       shuffle=shuffle, collate_fn=custom_collate)

    return train_dataloader, test_dataloader, validation_dataloader


if __name__ == "__main__":
    """
    just used for manual testing
    """
    dataset = ArxivDataset("database/dataset.db")
    train_dataloader = DataLoader(dataset, batch_size=200, shuffle=True, collate_fn=custom_collate)

    start = time.time()
    example = next(iter(train_dataloader))
    end = time.time()

    print("seconds", end - start)
