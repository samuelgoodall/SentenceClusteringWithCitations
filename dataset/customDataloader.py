from torch import Generator
from torch.utils.data import DataLoader, random_split, Subset

from dataset.ArxivDataset import ArxivDataset

class CustomDataLoader():
    @staticmethod
    def _custom_collate(batch: list):
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

    @staticmethod
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
        return DataLoader(dataset, batch_size=batch_size, shuffle=shuffle, collate_fn=CustomDataLoader._custom_collate)

    @staticmethod
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
            Generator that can be set for reproducable results
        dataset: ArxivDataset

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
                                      shuffle=shuffle, collate_fn=CustomDataLoader._custom_collate)
        test_dataloader = DataLoader(test_dataset, batch_size=batch_size,
                                     shuffle=shuffle, collate_fn=CustomDataLoader._custom_collate)
        validation_dataloader = DataLoader(validation_dataset, batch_size=batch_size,
                                           shuffle=shuffle, collate_fn=CustomDataLoader._custom_collate)

        return train_dataloader, test_dataloader, validation_dataloader

    @staticmethod
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

    @staticmethod
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
                                      shuffle=shuffle, collate_fn= CustomDataLoader._custom_collate)
        test_dataloader = DataLoader(Subset(dataset, test_idx), batch_size=batch_size,
                                     shuffle=shuffle, collate_fn= CustomDataLoader._custom_collate)
        validation_dataloader = DataLoader(Subset(dataset, val_idx), batch_size=batch_size,
                                           shuffle=shuffle, collate_fn= CustomDataLoader._custom_collate)

        return train_dataloader, test_dataloader, validation_dataloader
