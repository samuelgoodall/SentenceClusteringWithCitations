import sqlite3

import pandas as pd
import sqlalchemy
from sqlalchemy import text
from tqdm import tqdm

from dataset.database.database import (Citation, Paper, Paragraph, Sentence,
                                       SentenceCitationRelation,
                                       SQAlchemyDatabase)


class cutOutlierData:
    """class to delete database entries that are outlier data points"""
    def __init__(self, database_path):
        self.conn = sqlite3.connect(database_path)
        self.sql_session = SQAlchemyDatabase(database_path).session()

    def chunk_list(self, lst, chunk_size):
        """seperates a list into chunks"""
        for i in range(0, len(lst), chunk_size):
            yield lst[i:i + chunk_size]
    
    def log(self, string, number):
        """writes a string and number to txt file"""
        with open("log.txt", "a+") as file:
            file.write(string + str(number) + '\n')   
                 
    def find_long_papers(self):
        """finds the paragraph amount, where 95% percents of the papers have less paragraphs"""
        query = "SELECT paper_id, id FROM paragraph WHERE id IN (SELECT s.paragraph_id FROM sentence s JOIN sentence_citation_relation c ON s.id = c.sentence_id)"
        data = pd.read_sql_query(query, self.conn)
        grouped_data = data.groupby('paper_id')['id'].count()
        threshold = grouped_data.quantile(0.95)
        threshold = int(threshold)
        self.log("Threshold for paper length: ", threshold)
        return threshold

    def cut_long_papers(self):
        """deletes papers that have more paragraphs than a certain treshold and connected 
        paragraphs, sentences, citations and sentence-citation-relations from the database"""
        # select the paragraph IDs that satisfy the condition
        long_paper_ids = [result[0] for result in self.sql_session.query(Paragraph.paper_id)
                        .group_by(Paragraph.paper_id)
                        .having(sqlalchemy.func.count(Paragraph.id) > self.find_long_papers())]
        self.log("Number of papers to be deleted: ", len(long_paper_ids))
        
        for chunk in self.chunk_list(long_paper_ids, 1000):
            paragraphs_to_delete = self.sql_session.query(Paragraph).filter(Paragraph.paper_id.in_(chunk)).all()
            self.log("Number of paragraphs to be deleted in chunk: ", len(paragraphs_to_delete))
            
            paragraph_ids = [p.id for p in paragraphs_to_delete]
            sentences_to_delete = self.sql_session.query(Sentence).filter(Sentence.paragraph_id.in_(paragraph_ids)).all()
            self.log("Number of sentences to be deleted in chunk: ", len(sentences_to_delete))
            
            sentence_ids = [s.id for s in sentences_to_delete]
            citations_to_delete = self.sql_session.query(SentenceCitationRelation).filter(SentenceCitationRelation.sentence_id.in_(sentence_ids)).all()
            self.log("Number of citations to be deleted in chunk:", len(citations_to_delete))
            
            citation_ids = [c.citation_id for c in citations_to_delete]
            
            # delete the paragraphs and connected data
            for long_paper_id in tqdm(chunk):
                self.sql_session.query(Paragraph).filter_by(paper_id=long_paper_id).delete()
                self.sql_session.query(Paper).filter_by(id=long_paper_id).delete(synchronize_session=False) 
            
            # delete sentences connected to the paper
            for paragraph in paragraph_ids:
                self.sql_session.query(Sentence).filter_by(paragraph_id=paragraph).delete(synchronize_session=False)
            
            # delete citations connected to the sentence
            for sentence in sentence_ids:
                self.sql_session.query(SentenceCitationRelation).filter_by(sentence_id=sentence).delete()
            for citation in citation_ids:
                self.sql_session.query(Citation).filter_by(id=citation).delete()
            self.sql_session.commit()
        
    def find_long_paragraphs(self):
        """finds the sentence amount, where 95% percents of the paragraphs are have less sentences"""
        query = "SELECT s.id, paragraph_id FROM Sentence AS s WHERE s.id IN (SELECT c.sentence_id FROM sentence_citation_relation AS c)"
        data = pd.read_sql_query(query, self.conn)
        grouped_data = data.groupby('paragraph_id')['id'].count()
        threshold_paragraph = grouped_data.quantile(0.95)
        threshold_paragraph = int(threshold_paragraph)
        self.log("Threshold for paragraph length: ", threshold_paragraph)
        return threshold_paragraph

    def cut_long_paragraphs(self):
        """deletes paragraphs that have more sentences than a certain treshold and connected sentences,
        citations and sentence-citation-relations from the database"""
        # select the paragraph IDs that satisfy the condition
        long_paragraphs_ids = [result[0] for result in self.sql_session.query(Sentence.paragraph_id)
                        .group_by(Sentence.paragraph_id)
                        .having(sqlalchemy.func.count(Sentence.id) > self.find_long_paragraphs())]
        self.log("Number of paragraphs to be deleted: ", len(long_paragraphs_ids))
        
        for chunk in self.chunk_list(long_paragraphs_ids, 1000):
            paragraphs_to_delete = self.sql_session.query(Paragraph).filter(Paragraph.id.in_(chunk)).all()
            self.log("Number of paragraphs to be deleted in chunk: ", len(paragraphs_to_delete))
            
            paragraph_ids = [p.id for p in paragraphs_to_delete]
            sentences_to_delete = self.sql_session.query(Sentence).filter(Sentence.paragraph_id.in_(paragraph_ids)).all()
            self.log("Number of sentences part of paragraphs in chunk: ", len(sentences_to_delete))
            
            sentence_ids = [s.id for s in sentences_to_delete]
            citations_to_delete = self.sql_session.query(SentenceCitationRelation).filter(SentenceCitationRelation.sentence_id.in_(sentence_ids)).all()
            self.log("Number of citations part of sentences in chunk:", len(citations_to_delete))
            
            citation_ids = [c.citation_id for c in citations_to_delete]
            
            # delete the paragraphs and connected data       
            # delete sentences connected to the paragraph
            for paragraph in paragraph_ids:
                self.sql_session.query(Paragraph).filter_by(id=paragraph).delete(synchronize_session=False)
                self.sql_session.query(Sentence).filter_by(paragraph_id=paragraph).delete(synchronize_session=False)
            
            # delete citations connected to the sentence
            for sentence in sentence_ids:
                self.sql_session.query(SentenceCitationRelation).filter_by(sentence_id=sentence).delete()
            for citation in citation_ids:
                self.sql_session.query(Citation).filter_by(id=citation).delete()
            self.sql_session.commit()
            self.delete_papers_without_paragraph()

    def delete_papers_without_paragraph(self):
        """delete papers from the database, that are connected to no paragraph in the database"""
        papers = self.sql_session.execute(text("DELETE FROM paper WHERE id NOT IN (SELECT DISTINCT paper_id FROM paragraph)"))
        num_deleted = papers.rowcount
        self.log("Number of papers to be deleted: ", num_deleted)
        self.sql_session.commit()   
        
    def find_long_sentence(self):
        """finds the word amount, where 95% percent of the sentences have less words"""
        query = "SELECT s.id, paragraph_id, content FROM Sentence AS s WHERE s.id IN (SELECT c.sentence_id FROM sentence_citation_relation AS c)"
        data = pd.read_sql_query(query, self.conn)
        token_count = data['content'].apply(lambda x: len(x.split()))
        threshold_sentence = token_count.quantile(0.95)
        threshold_sentence = int(threshold_sentence)
        self.log("Threshold for sentence length: ", threshold_sentence)
        return threshold_sentence

    def cut_long_short_sentences(self):
        """deletes sentences that have more words than a certain treshold and less than 3 words from the database"""
        threshold = self.find_long_sentence()
        sentences_long = self.sql_session.execute(text("DELETE FROM Sentence WHERE LENGTH(content) - LENGTH(REPLACE(content, ' ', '')) + 1 > :threshold;"), {'threshold': threshold})
        sentences_short = self.sql_session.execute(text("DELETE FROM Sentence WHERE LENGTH(content) - LENGTH(REPLACE(content, ' ', '')) + 1 < 3;"))
        num_deleted_long = sentences_long.rowcount
        num_deleted_short = sentences_short.rowcount
        self.log("Number of long sentences to be deleted: ", num_deleted_long)
        self.log("Number of short sentences to be deleted: ", num_deleted_short)
        self.sql_session.commit()
        self.delete_paragraphs_without_sentence()
        self.delete_papers_without_paragraph()
        self.delete_citations_without_sentence()

    def delete_paragraphs_without_sentence(self):
        """delete paragraphs from database, that are connected to no sentence in the database"""
        paragraphs = self.sql_session.execute(text("DELETE FROM paragraph WHERE id NOT IN (SELECT DISTINCT paragraph_id FROM sentence)"))
        num_deleted = paragraphs.rowcount
        self.log("Number of paragraphs to be deleted: ", num_deleted)
        self.sql_session.commit()   
        
    def delete_citations_without_sentence(self):
        """delete citations and sentence-citation-relations from database, that are connected to no sentence in the database"""
        self.sql_session.execute(text("DELETE FROM sentence_citation_relation WHERE sentence_id NOT IN (SELECT DISTINCT id FROM sentence)"))
        citations = self.sql_session.execute(text("DELETE FROM citation WHERE id NOT IN (SELECT DISTINCT citation_id FROM sentence_citation_relation)"))
        num_deleted = citations.rowcount
        self.log("Number of citations to be deleted: ", num_deleted)
        self.sql_session.commit()   

    def find_sentences_with_many_citations(self):
        """finds the citation amount, where 95% percent of the sentences have less citations"""
        data = pd.read_sql_query('SELECT * FROM "sentence_citation_relation"', self.conn)
        grouped_data = data.groupby('sentence_id')['citation_id'].count()
        threshold_citations = grouped_data.quantile(0.95)
        threshold_citations= int(threshold_citations)
        self.log("Threshold for citation amount: ", threshold_citations)
        return threshold_citations

    def cut_many_citations(self):
        """deletes sentences that have more citations than a certain treshold and connected citations and sentence-citation relations
        from the database"""
        # select the sentence IDs that satisfy the condition
        many_citations_sentence_ids = [result[0] for result in self.sql_session.query(SentenceCitationRelation.sentence_id)
                        .group_by(SentenceCitationRelation.sentence_id)
                        .having(sqlalchemy.func.count(SentenceCitationRelation.citation_id) > self.find_sentences_with_many_citations())]
        self.log("Number of sentences to be deleted: ", len(many_citations_sentence_ids))
        
        for chunk in self.chunk_list(many_citations_sentence_ids, 1000):
            sentences_to_delete = self.sql_session.query(SentenceCitationRelation).filter(SentenceCitationRelation.sentence_id.in_(chunk)).all()
            self.log("Number of citations to be deleted in chunk: ", len(sentences_to_delete))
            
            sentence_ids = [s.sentence_id for s in sentences_to_delete] 
            citation_ids = [c.citation_id for c in sentences_to_delete]
        
            # delete the sentences and citations      
            for sentence in sentence_ids:
                self.sql_session.query(Sentence).filter_by(id=sentence).delete(synchronize_session=False)
                self.sql_session.query(SentenceCitationRelation).filter_by(sentence_id=sentence).delete()

            for citation in citation_ids:
                self.sql_session.query(Citation).filter_by(id=citation).delete()
            self.sql_session.commit()
            self.delete_paragraphs_without_sentence()
            self.delete_papers_without_paragraph()
            
    def log_total(self):
        """log the amount of papers, paragraphs, sentences, citations and sentence-citation-relations in the database"""
        cursor = self.conn.cursor()
        query = "SELECT COUNT(id) FROM paper;"
        cursor.execute(query)
        papers = cursor.fetchone()[0]
        self.log("Total papers: ", papers)
        
        query = "SELECT COUNT(id) FROM paragraph;"
        cursor.execute(query)
        paragraphs = cursor.fetchone()[0]
        self.log("Total paragraphs: ", paragraphs)
        
        query = "SELECT COUNT(id) FROM sentence;"
        cursor.execute(query)
        sentences = cursor.fetchone()[0]
        self.log("Total sentences: ", sentences)
        
        query = "SELECT COUNT(id) FROM citation;"
        cursor.execute(query)
        citations = cursor.fetchone()[0]
        self.log("Total citations: ", citations)
        
        query = "SELECT COUNT(citation_id) FROM sentence_citation_relation;"
        cursor.execute(query)
        sentence_citations_relations = cursor.fetchone()[0]
        self.log("Total sentence-citations-relations: ", sentence_citations_relations)

        cursor.close()
        
    def run(self):
        """delete long papers, paragraphs, sentences, and sentences with many citations, and all connected data from database
        and log the the size of the database tables at each step"""    
        self.cut_long_papers()
        self.log("After Paper deletion: ", "")
        self.log_total()
        self.log("\n", "")
        self.cut_long_paragraphs()
        self.log("After Paragraph deletion: ", "")
        self.log_total()
        self.log("\n", "")
        self.cut_long_short_sentences()
        self.log("After Sentence deletion: ", "")
        self.log_total()
        self.log("\n", "")
        self.cut_many_citations()
        self.log("After Citation deletion: ", "")
        self.log_total()
        self.conn.close()
        
if __name__ == "__main__":
    test = cutOutlierData('dataset/database/dataset.db')
    test.run()
