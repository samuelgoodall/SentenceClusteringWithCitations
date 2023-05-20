import pickle
import sqlite3

from tqdm import tqdm

from dataset.database.database import SQAlchemyDatabase, Paper as oldPaper
from dataset.database.database_indexes_python import add_indexes
from dataset.database.database_precomputed_embeddings import SQAlchemyDatabasePrecomputedEmbeddings, Paper, Citation, \
    Sentence, Paragraph
from experiments.embedding_methods.bert_embedding import BertTransformerEmbedding
from experiments.embedding_methods.embedding_interface import EmbeddingInterface
from experiments.embedding_methods.sbert_embedding import SentenceTransformerEmbedding


def add_new_paper(session, paper_title="", paper_authors=""):
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


def create_new_sentence(new_paragraph, sentence_content: str, content_embedded):
    new_sentence = Sentence(content=sentence_content, content_embedded=content_embedded)
    new_sentence.paragraph = new_paragraph
    return new_sentence


def create_new_citation(title: str, author: str, abstract: str, new_sentence: Sentence, content_embedded):
    new_citation = Citation(title=title, author=str(author), abstract=abstract, title_embedded=content_embedded)
    new_sentence.citations.append(new_citation)
    return new_citation


def create_embedded_dataset(db_path_old: str, db_path_new: str, embedding: EmbeddingInterface):
    sql_session_new = SQAlchemyDatabasePrecomputedEmbeddings(db_path_new).session()
    sql_session_old = SQAlchemyDatabase(db_path_old).session()

    all_papers = sql_session_old.query(oldPaper).all()

    for paper in tqdm(all_papers):
        new_paper = add_new_paper(paper_title=paper.title, paper_authors=paper.authors, session=sql_session_new)
        sql_session_new.add(new_paper)
        sql_session_new.commit()
        for paragraph in paper.paragraphs:
            new_paragraph = create_new_paragraph(paper=new_paper)
            for sentence in paragraph.sentences:

                embedded_content = embedding.embed_sentence(sentence.content)
                pickled_content = sqlite3.Binary(pickle.dumps(embedded_content, pickle.HIGHEST_PROTOCOL))

                new_sentence = create_new_sentence(new_paragraph, sentence.content, pickled_content)
                for citation in sentence.citations:
                    embedded_content = embedding.embed_sentence(citation.title)
                    pickled_content = sqlite3.Binary(pickle.dumps(embedded_content, pickle.HIGHEST_PROTOCOL))
                    create_new_citation(title=citation.title, author=citation.author, abstract=citation.abstract,
                                        new_sentence=new_sentence, content_embedded=pickled_content)

    sql_session_new.commit()
    add_indexes(db_path_new)


def main():
    print("query done!")
    db_path_new_sbert = "../dataset/database/dataset_new_precomputed_embeddings_sbert.db"
    db_path_new_bert = "../dataset/database/dataset_new_precomputed_embeddings_bert.db"
    db_path_old = "../dataset/database/dataset_new.db"
    sbert_embedding = SentenceTransformerEmbedding("all-mpnet-base-v2")
    bert_embedding = BertTransformerEmbedding("bert-base-uncased")
    create_embedded_dataset(db_path_old=db_path_old, db_path_new=db_path_new_sbert, embedding=sbert_embedding)
    create_embedded_dataset(db_path_old=db_path_old, db_path_new=db_path_new_bert, embedding=bert_embedding)


if __name__ == "__main__":
    main()
