from sqlalchemy import Column, ForeignKey, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

engine = create_engine('sqlite:///database/dataset.db', echo=True)
Base = declarative_base()
_SessionFactory = sessionmaker(bind=engine)

def session_factory():
    Base.metadata.create_all(engine)
    return _SessionFactory()

class Citation(Base):
    """
    Citation class to save citation information from the sentences in the paper.  
    """
    __tablename__ = 'citation'
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String)
    author = Column(String)

    
    def __init__(self, title:str, author:str):
        """ Initialize the Citation class.
        Args:
            title (str): Title of the citation.
            author (str): Author of the citation.
        """
        self.title = title
        self.author = author
        
class Sentence(Base):
    """Sentence class to save sentence information."""
    __tablename__ = 'sentence'
    id = Column(Integer, primary_key=True)
    content = Column(String)
    citations = relationship("Citation", secondary="sentence_citation_relation")
    paragraph = relationship("Paragraph", back_populates="sentences")
    paragraph_id = Column(Integer, ForeignKey('paragraph.id'))
    
    def __init__(self, content:str):
        """ Initialize the Sentence class.
        Args:
            content (str): Letter of the sentence.
        """
        self.content = content

class SentenceCitationRelation(Base):
    """SentenceCitationRelation class to save the n to m relationship between sentence and citation."""
    __tablename__ = 'sentence_citation_relation'   
    sentence_id = Column(Integer, ForeignKey('sentence.id'), primary_key=True)
    citation_id = Column(Integer, ForeignKey('citation.id'), primary_key=True)
        
class Paper(Base):
    """Paper class to save paper information."""
    __tablename__ = 'paper'
    
    id = Column(Integer, primary_key=True)
    #meta_data_id = Column(Integer, ForeignKey('metadata.id'))
    #meta_data = relationship("metadata", back_populates="paper")
    title = Column(String)
    authors = Column(String)

class Paragraph(Base):
    """Paragraph class to save paragraph information."""
    __tablename__ = 'paragraph'
    id = Column(Integer, primary_key=True)
    sentences = relationship("Sentence", back_populates="paragraph")
