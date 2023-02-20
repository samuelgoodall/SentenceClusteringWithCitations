import os
import time

import pandas as pd

from database.database import Paper
from database.database import SQAlchemyDatabase


def add_new_paper(session, paper_title, paper_authors):
    paper = (
        session.query(Paper)
        .filter(Paper.title == paper_title)
        .one_or_none()
    )

    # TODO log Warning that paper is already in db!
    if paper is not None:
        return

    paper = Paper(title=paper_title, authors=paper_authors)
    session.add(paper)
    session.commit()


def main():
    abs_path = os.path.abspath("database/dataset.db")
    session = SQAlchemyDatabase(abs_path).session
    paper = Paper()
    return

    print("hello World")
    start = time.time()
    chunk = pd.read_csv('output/data0.csv', chunksize=10000)
    end = time.time()
    print("Read csv with chunks: ", (end - start), "sec")

    start = time.time()
    df = pd.concat(chunk)
    end = time.time()
    print("Concatenated csv with chunks: ", (end - start), "sec")
    # print(df.to_string())
    print(df.iterrows())


if __name__ == "__main__":
    main()