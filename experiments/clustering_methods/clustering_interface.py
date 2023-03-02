import abc


class ClusteringInterface(metaclass=abc.ABCMeta):
    @classmethod
    def __subclasshook__(cls, subclass):
        return (hasattr(subclass, 'cluster_sentences') and
                callable(subclass.cluster_sentences) and
                hasattr(subclass,'return_hyper_params') and
                callable(subclass.return_hyper_params) or
                NotImplemented)

    @abc.abstractmethod
    def cluster_sentences(self, sentences: list):
        """clusters sentences"""
        raise NotImplementedError

    @abc.abstractmethod
    def return_hyper_params(self):
        """returns the hyperparameters used as json"""
        raise NotImplementedError



