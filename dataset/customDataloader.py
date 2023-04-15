import sqlite3
import time

from torch import Generator
from torch.utils.data import Dataset, DataLoader, random_split, Subset

from dataset.database.database import SQAlchemyDatabase, Paper
from dataclasses import dataclass


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


def get_dataloader(batch_size: int = 20, shuffle: bool = False, dataset: ArxivDataset = None):
    """
    gets the dataloader on the whole dataset

    Parameters
    ----------
    batch_size : int
        The size of the batch = how many examples are fetched
    shuffle : bool
        Sets wether dataloader shall shuffle the data whilst iterating
    dataset: ArxivDataset
       the ArxivDataset
    Returns
    -------
    DataLoader
       DataLoader for the whole Dataset
    """
    return DataLoader(dataset, batch_size=batch_size, shuffle=shuffle, collate_fn=custom_collate)


def get_train_test_validation_dataloader(batch_size: int = 20, shuffle: bool = True,
                                         train_test_validation_split: list[float] = [],
                                         fixed_random_generator: Generator = None, dataset: ArxivDataset = None):
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
    fixed_random_generator : Generator
        generator that can be set for reproducable results

    Returns
    -------
    tuple[DataLoader]
        the train,test and validation dataloader

    Raises
    ------
    ValueError
        If train_test_validation split is malformed
    """

    if len(train_test_validation_split) < 3 or train_test_validation_split is None:
        raise ValueError("train_test_validation_split must be given! has to be array/list of floats that sum up to 1!")

    if sum(train_test_validation_split) != 1.0:
        raise ValueError("train_test_validation_split values have to sum up to 1!")

    if fixed_random_generator is None:
        train_dataset, test_dataset, validation_dataset = random_split(dataset,
                                                                       train_test_validation_split)
    else:
        train_dataset, test_dataset, validation_dataset = random_split(dataset,
                                                                       train_test_validation_split,
                                                                       generator=fixed_random_generator)
    train_dataloader = DataLoader(train_dataset, batch_size=batch_size,
                                  shuffle=shuffle, collate_fn=custom_collate)
    test_dataloader = DataLoader(test_dataset, batch_size=batch_size,
                                 shuffle=shuffle, collate_fn=custom_collate)
    validation_dataloader = DataLoader(validation_dataset, batch_size=batch_size,
                                       shuffle=shuffle, collate_fn=custom_collate)

    return train_dataloader, test_dataloader, validation_dataloader


def get_train_test_validation_index_split(train_test_validation_split: list[float] = [],
                                          fixed_random_generator: Generator = None, dataset: ArxivDataset = None):
    """
    gets the train,test,validation indexes needed for reproducable datasetsplits

    Parameters
    ----------
    train_test_validation_split : list[float]
        The ratio of train test and validation split of the whole dataset, list of floats has to sum to 1
    fixed_random_generator : Generator
        generator that can be set for reproducable results
    dataset: ArxivDataset
            the Dataset to be partitioned

    Returns
    -------
    tuple[list[int]]
        the train,test and validation index lists

    Raises
    ------
    ValueError
        If train_test_validation split is malformed
    """

    if len(train_test_validation_split) < 3 or train_test_validation_split is None:
        raise ValueError("train_test_validation_split must be given! has to be array/list of floats that sum up to 1!")

    if sum(train_test_validation_split) != 1.0:
        raise ValueError("train_test_validation_split values have to sum up to 1!")

    if fixed_random_generator is None:
        train_dataset, test_dataset, validation_dataset = random_split(dataset,
                                                                       train_test_validation_split)
    else:
        train_dataset, test_dataset, validation_dataset = random_split(dataset,
                                                                       train_test_validation_split,
                                                                       generator=fixed_random_generator)
    return train_dataset.indices, test_dataset.indices, validation_dataset.indices


def get_train_test_validation_split_indexbased_dataloader(train_idx=[], test_idx=[], val_idx=[], batch_size: int = 20,
                                                          shuffle: bool = True, dataset: ArxivDataset = None):
    """
    gets the dataloaders for train test and validation based on three arrays with indexes

    Parameters
    ----------
    train_idx: list<int>
        the indexes belonging to the train subset of the dataset
    test_idx: list<int>
        the indexes belonging to the test subset of the dataset
    val_idx: list<int>
        the indexes belonging to the validation subset of the dataset
    batch_size : int
        The size of the batch = how many examples are fetched
    shuffle : bool
        Sets wether dataloader shall shuffle the data whilst iterating
    dataset: ArxivDataset
        the Dataset to be partitioned

    Returns
    -------
    tuple[DataLoader]
        the train,test and validation dataloader

    """

    train_dataloader = DataLoader(Subset(dataset, train_idx), batch_size=batch_size,
                                  shuffle=shuffle, collate_fn=custom_collate)
    test_dataloader = DataLoader(Subset(dataset, test_idx), batch_size=batch_size,
                                 shuffle=shuffle, collate_fn=custom_collate)
    validation_dataloader = DataLoader(Subset(dataset, val_idx), batch_size=batch_size,
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
