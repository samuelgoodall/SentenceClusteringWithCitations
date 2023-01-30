from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from .base import Base
from .citation import Citation


class Sentence(Base):
    """Sentence class to save sentence information."""
    __tablename__ = 'sentence'
    id = Column(Integer, primary_key=True)
    content = Column(String)
    #citations = relationship(Citation, secondary="sentence_citation_relation")
    def __init__(self, content:str):
        """Initialize a Sentence object.

        Args:
            content (str): letters of the sentence.
        """
        self.content = content
        