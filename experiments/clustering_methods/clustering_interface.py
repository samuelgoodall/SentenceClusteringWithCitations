import abc


class ClusteringInterface(metaclass=abc.ABCMeta):
    @classmethod
    def __subclasshook__(cls, subclass):
        return (hasattr(subclass, 'cluster_sentences') and
                callable(subclass.cluster_sentences) or NotImplemented)

    @abc.abstractmethod
    def cluster_sentences(self, sentences: list):
        """clusters sentences"""
        raise NotImplementedError



