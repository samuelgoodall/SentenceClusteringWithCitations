from sqlalchemy import Column, Identity, Integer, String
from sqlalchemy.orm import relationship

from .base import Base

class Citation(Base):
    """
    Citation class to save citation information from the sentences in the paper.  
    """
    __tablename__ = 'citation'
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String)
    author = Column(String)
    
    def __init__(self, title:str, author:str):
        """Initialize a Citation object.

        Args:
            title (str): Title of the mentioned paper.
            author (str): Author of the mentioned paper.
        """
        self.title = title
        self.author = author
        