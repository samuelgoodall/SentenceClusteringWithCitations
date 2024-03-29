import sqlite3

from sqlalchemy import Column, ForeignKey, Integer, String, create_engine, UniqueConstraint, LargeBinary
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

Base = declarative_base()


class SQAlchemyDatabasePrecomputedEmbeddings:
    def __init__(self, database_path):
        self.engine = create_engine('sqlite:///' + database_path, echo=False)
        self.session = sessionmaker(bind=self.engine)
        self.base = Base
        self.base.metadata.create_all(self.engine)


class Citation(Base):
    """
    Citation class to save citation information from the sentences in the paper.  
    """
    __tablename__ = 'citation'
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String)
    title_embedded = Column(LargeBinary)
    author = Column(String)
    abstract = Column(String)

    def __init__(self, title: str, author: str, abstract: str, title_embedded: LargeBinary):
        """ Initialize the Citation class.
        Args:
            title (str): Title of the citation.
            author (str): Author of the citation.
        """
        self.title = title
        self.author = author
        self.abstract = abstract
        self.title_embedded = title_embedded

class Sentence(Base):
    """Sentence class to save sentence information."""
    __tablename__ = 'sentence'
    id = Column(Integer, primary_key=True)
    content = Column(String)
    content_embedded = Column(LargeBinary)
    citations = relationship("Citation", secondary="sentence_citation_relation")
    paragraph = relationship("Paragraph", back_populates="sentences")
    paragraph_id = Column(Integer, ForeignKey('paragraph.id'))

    def __init__(self, content: str, content_embedded: LargeBinary):
        """ Initialize the Sentence class.
        Args:
            content (str): Letter of the sentence.
        """
        self.content = content
        self.content_embedded = content_embedded


class SentenceCitationRelation(Base):
    """SentenceCitationRelation class to save the n to m relationship between sentence and citation."""
    __tablename__ = 'sentence_citation_relation'
    sentence_id = Column(Integer, ForeignKey('sentence.id'), primary_key=True)
    citation_id = Column(Integer, ForeignKey('citation.id'), primary_key=True)


class Paper(Base):
    """Paper class to save paper information."""
    __tablename__ = 'paper'

    id = Column(Integer, primary_key=True)
    # meta_data_id = Column(Integer, ForeignKey('metadata.id'))
    # meta_data = relationship("metadata", back_populates="paper")
    title = Column(String)
    authors = Column(String)
    paragraphs = relationship("Paragraph", back_populates="paper")


class Paragraph(Base):
    """Paragraph class to save paragraph information."""
    __tablename__ = 'paragraph'
    id = Column(Integer, primary_key=True)
    sentences = relationship("Sentence", back_populates="paragraph")
    paper = relationship("Paper", back_populates="paragraphs")
    paper_id = Column(Integer, ForeignKey('paper.id'))
