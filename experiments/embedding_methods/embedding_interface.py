import abc


class EmbeddingInterface(metaclass=abc.ABCMeta):
    @classmethod
    def __subclasshook__(cls, subclass):
        return (hasattr(subclass, 'embed_sentence') and
                callable(subclass.embed_sentence) and
                hasattr(subclass,'return_hyper_params') and
                callable(subclass.return_hyper_params) or NotImplemented)

    @abc.abstractmethod
    def embed_sentence(self, sentence: str):
        """embeds the sentence"""
        raise NotImplementedError

    @abc.abstractmethod
    def return_hyper_params(self)->dict:
        """returns the hyperparameters used as dict"""
        raise NotImplementedError