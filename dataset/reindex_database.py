import os.path

import spacy
from tqdm import tqdm
from dataset.database.database import SQAlchemyDatabase, Paper, Paragraph, Sentence, Citation

def add_new_paper(session,paper_title="", paper_authors=""):
    paper = (
        session.query(Paper)
        .filter(Paper.title == paper_title)
        .one_or_none()
    )
    if paper is not None:
        return paper

    paper = Paper(title=paper_title, authors=paper_authors)
    return paper


def create_new_paragraph(paper: Paper):
    new_paragraph = Paragraph()
    new_paragraph.paper = paper
    return new_paragraph


def create_new_sentence(new_paragraph, sentence_content: str):
    new_sentence = Sentence(content=sentence_content)
    new_sentence.paragraph = new_paragraph
    return new_sentence


def create_new_citation(title: str, author: str, abstract: str, new_sentence: Sentence):
    new_citation = Citation(title=title, author=str(author), abstract=abstract)
    new_sentence.citations.append(new_citation)
    return new_citation

def create_reindexed_dataset():
    db_path_new = "database/dataset_new.db"
    db_path_old = os.path.abspath("database/dataset.db")

    sql_session_new = SQAlchemyDatabase(db_path_new).session()
    sql_session_old = SQAlchemyDatabase(db_path_old).session()

    all_papers = sql_session_old.query(Paper).all()
    for paper in tqdm(all_papers):
        new_paper = add_new_paper(paper_title=paper.title, paper_authors=paper.authors, session=sql_session_new)
        sql_session_new.add(new_paper)
        sql_session_new.commit()
        for paragraph in paper.paragraphs:
            new_paragraph = create_new_paragraph(paper=new_paper)
            for sentence in paragraph.sentences:
                new_sentence = create_new_sentence(new_paragraph, sentence.content)
                for citation in sentence.citations:
                    create_new_citation(title=citation.title, author=citation.author, abstract=citation.abstract,
                                        new_sentence=new_sentence)
    sql_session_new.commit()

def create_lemmatized_dataset():
    spacy.require_gpu()
    spacy_model = spacy.load("en_core_web_trf")

    db_path_new = "database/dataset_new_lemmatized.db"
    db_path_old = os.path.abspath("database/dataset.db")

    sql_session_new = SQAlchemyDatabase(db_path_new).session()
    sql_session_old = SQAlchemyDatabase(db_path_old).session()

    all_papers = sql_session_old.query(Paper).all()
    for paper in tqdm(all_papers):
        new_paper = add_new_paper(paper_title=paper.title, paper_authors=paper.authors, session=sql_session_new)
        sql_session_new.add(new_paper)
        for paragraph in paper.paragraphs:
            sql_session_new.commit()
            new_paragraph = create_new_paragraph(paper=new_paper)
            for sentence in paragraph.sentences:
                doc = spacy_model(sentence.content.lower())
                lemmatized_sentence = " ".join([token.lemma_ for token in doc])
                new_sentence = create_new_sentence(new_paragraph,lemmatized_sentence)
                for citation in sentence.citations:
                    doc = spacy_model(citation.title.lower())
                    lemmatized_title = " ".join([token.lemma_ for token in doc])
                    create_new_citation(title=lemmatized_title, author=citation.author, abstract=citation.abstract,
                                        new_sentence=new_sentence)
    sql_session_new.commit()
def main():
    create_reindexed_dataset()
    create_lemmatized_dataset()
    print("query done!")



if __name__ == "__main__":
    main()