import abc


class EmbeddingInterface(metaclass=abc.ABCMeta):
    @classmethod
    def __subclasshook__(cls, subclass):
        return (hasattr(subclass, 'embed_sentence') and
                callable(subclass.embed_sentence) or NotImplemented)

    @abc.abstractmethod
    def embed_sentence(self, sentence: str):
        """embeds the sentence"""
        raise NotImplementedError
