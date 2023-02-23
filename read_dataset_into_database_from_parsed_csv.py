import os
import time

import pandas as pd
from tqdm import tqdm, tqdm_pandas

from database.database import Paper, Paragraph, Sentence
from database.database import SQAlchemyDatabase


def add_new_paper(session, paper_title="", paper_authors=""):
    paper = (
        session.query(Paper)
        .filter(Paper.title == paper_title)
        .one_or_none()
    )

    #TODO log if paper already exists!
    if paper is not None:
        return paper

    paper = Paper(title=paper_title, authors=paper_authors)
    session.add(paper)
    session.commit()
    return paper


def convert_row_to_db_entry(row, session):
    #print("ROW \n", row["Foldername"])
    new_paper = add_new_paper(session, paper_title=row["Foldername"], paper_authors="")
    new_paragraph = Paragraph()
    new_paragraph.paper = new_paper
    new_sentence = Sentence(content=row["sentence"])
    new_sentence.paragraph = new_paragraph
    session.add(new_paper)
    session.commit()
    return row


def main():
    """
    abs_path = os.path.abspath("database/dataset.db")
    session = SQAlchemyDatabase(abs_path).session()
    new_paper = Paper(title="MYTITLE",authors="Authors,fdasj")
    new_paragraph = Paragraph()
    new_paragraph.paper = new_paper
    session.add(new_paper)
    new_sentence = Sentence(content="Sentence VERY important!")
    new_sentence.paragraph = new_paragraph
    session.commit()
    """
    tqdm().pandas()

    abs_path = os.path.abspath("database/dataset.db")
    session = SQAlchemyDatabase(abs_path).session()

    start = time.time()
    chunk = pd.read_csv('output/data0.csv', chunksize=10000)
    end = time.time()
    print("Read csv with chunks: ", (end - start), "sec")

    start = time.time()
    df = pd.concat(chunk)
    end = time.time()
    print("Concatenated csv with chunks: ", (end - start), "sec")
    print(df.columns)
    df.progress_apply(lambda row: convert_row_to_db_entry(row, session), axis=1)


if __name__ == "__main__":
    main()
