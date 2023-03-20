import sqlite3

import matplotlib.pyplot as plt
import pandas as pd


class descriptiveStatistics:
    """class to calculate descriptive statistics on a database"""
    def __init__(self, database_path):
        self.conn = sqlite3.connect(database_path)
        
    def log(self, string, number):
        with open("descriptive_statistic/descriptive_statistics.txt", "a+") as file:
            file.write(string + str(number) + "\n") 
    
    def analyze_paragraphs_per_paper(self):
        """calculate descriptive statistics on number of paragraphs per paper and save boxplot and histogram"""
        query = "SELECT paper_id, id FROM paragraph WHERE id IN (SELECT s.paragraph_id FROM sentence s JOIN sentence_citation_relation c ON s.id = c.sentence_id)"
        data = pd.read_sql_query(query, self.conn)
        grouped_data = data.groupby('paper_id')['id'].count()
        mean_paragraphs_per_paper = grouped_data.mean()
        self.log('Average paragraphs per paper:', mean_paragraphs_per_paper)
        min_paragraphs_per_paper = grouped_data.min()
        self.log('Minimum paragraphs per paper:', min_paragraphs_per_paper)
        max_paragraphs_per_paper = grouped_data.max()
        self.log('Maximum paragraphs per paper:', max_paragraphs_per_paper)
        sd_paragraphs_per_paper = grouped_data.std()
        self.log('Standard deviation:', sd_paragraphs_per_paper)
        num_paper = data['paper_id'].nunique()
        self.log("Number of Papers: ", num_paper)
        #boxplot
        fig, ax = plt.subplots()
        ax.boxplot(grouped_data.values, whis=1.5)
        ax.set_ylim([0, 11])
        ax.set_title('Distribution of Paragraphs per Paper')
        ax.set_xlabel('Paper')
        ax.set_ylabel('Number of Paragraphs')
        plt.savefig('descriptive_statistic/plots/paragraphDistributionBP.png')
        plt.show()
        #create histogram
        fig, ax = plt.subplots()
        ax.hist(grouped_data.values, bins=10)
        ax.set_xlim([0, 10])
        ax.set_title('Distribution of Paragraphs per Paper')
        ax.set_xlabel('Number of Paragraphs')
        ax.set_ylabel('Number of Papers')
        plt.savefig('descriptive_statistic/plots/paragraphDistributionHist.png')
        plt.show()
        #create table
        paper_counts = grouped_data.value_counts().sort_index()
        table = pd.DataFrame({
            'Number of paragraphs': paper_counts.index,
            'Number of papers': paper_counts.values
        })
        table.to_csv('descriptive_statistic/tables/paragraphs_per_paper.csv', index=False)

    def analyze_sentences_per_paragraph(self):
        """calculate descriptive statistics on number sentences per paragraph and save boxplot and histogram"""
        query = "SELECT s.id, paragraph_id FROM Sentence AS s WHERE s.id IN (SELECT c.sentence_id FROM sentence_citation_relation AS c)"
        data = pd.read_sql_query(query, self.conn)
        grouped_data = data.groupby('paragraph_id')['id'].count()
        mean_sentence_per_paragraph = grouped_data.mean()
        self.log('Average sentences per paragraph:', mean_sentence_per_paragraph)
        min_sentence_per_paragraph = grouped_data.min()
        self.log('Minimum sentences per paragraph:', min_sentence_per_paragraph)
        max_sentence_per_paragraph = grouped_data.max()
        self.log('Maximum sentences per paragraph:', max_sentence_per_paragraph)
        sd_sentence_per_paragraph = grouped_data.std()
        self.log('Standard deviation:', sd_sentence_per_paragraph)
        num_paragraphs = data['paragraph_id'].nunique()
        self.log('Number of paragraphs with sentence:', num_paragraphs)
        #boxplot
        fig, ax = plt.subplots()
        ax.boxplot(grouped_data.values, whis=1.5)
        ax.set_ylim([0, 7])
        ax.set_title('Distribution of Sentences per Paragraph')
        ax.set_xlabel('Paragraph')
        ax.set_ylabel('Number of Sentences')
        plt.savefig('descriptive_statistic/plots/sentenceDistributionBP.png')
        plt.show()
        #create histogram
        fig, ax = plt.subplots()
        ax.set_title('Distribution of Sentences per Paragraph')
        ax.hist(grouped_data.values, bins=6)
        ax.set_xlim([0, 6])
        ax.set_xlabel('Number of Sentences')
        ax.set_ylabel('Number of Paragraphs')
        plt.savefig('descriptive_statistic/plots/sentenceDistributionHist.png')
        plt.show()
        #create table
        paragraph_counts = grouped_data.value_counts().sort_index()
        table = pd.DataFrame({
            'Number of sentences': paragraph_counts.index,
            'Number of paragraph': paragraph_counts.values
        })
        table.to_csv('descriptive_statistic/tables/sentence_per_paragraph.csv', index=False)

    def analyze_citations_per_sentence(self):
        """calculate descriptive statistics on citations per sentence and save boxplot and histogram"""
        data = pd.read_sql_query('SELECT * FROM "sentence_citation_relation"', self.conn)
        grouped_data = data.groupby('sentence_id')['citation_id'].count()
        mean_citation_per_sentences = grouped_data.mean()
        self.log('Average citations per sentence:', mean_citation_per_sentences)
        min_citation_per_sentences = grouped_data.min()
        self.log('Minimum citations per sentence:', min_citation_per_sentences)
        max_citation_per_sentences = grouped_data.max()
        self.log('Maximum citations per sentence:', max_citation_per_sentences)
        sd_citation_per_sentences = grouped_data.std()
        self.log('Standard deviation:', sd_citation_per_sentences)
        num_sentences = data['sentence_id'].nunique()
        self.log('Number of sentence with citations:', num_sentences)
        #boxplot
        fig, ax = plt.subplots()
        ax.boxplot(grouped_data.values, whis=1.5)
        ax.set_ylim([0, 6])
        ax.set_title('Distribution of Citations per Sentence')
        ax.set_xlabel('Sentence')
        ax.set_ylabel('Number of Citations')
        plt.savefig('descriptive_statistic/plots/citationDistributionBP.png')
        plt.show()
        #create histogram
        fig, ax = plt.subplots()
        ax.set_title('Distribution of Citations per Sentence')
        ax.hist(grouped_data.values, bins=5)
        ax.set_xlim([0, 5])
        ax.set_xlabel('Number of Citations')
        ax.set_ylabel('Number of Sentences')
        plt.savefig('descriptive_statistic/plots/citationDistributionHist.png')
        plt.show()
        #create table
        sentence_counts = grouped_data.value_counts().sort_index()
        table = pd.DataFrame({
            'Number of citations': sentence_counts.index,
            'Number of sentences': sentence_counts.values
        })
        table.to_csv('descriptive_statistic/tables/citation_per_sentence.csv', index=False)
   
    def analyze_sentence_length(self):
        """calculate descriptive statistics on words per sentence and save boxplot and histogram"""
        query = "SELECT s.id, paragraph_id, content FROM Sentence AS s WHERE s.id IN (SELECT c.sentence_id FROM sentence_citation_relation AS c)"
        data = pd.read_sql_query(query, self.conn)
        sentence_lengths = data['content'].apply(lambda x: len(x.split()))
        average_length = sentence_lengths.mean()
        self.log('Average sentence length:', average_length)
        std_length = sentence_lengths.std()
        self.log('Standard deviation of sentence length:', std_length)
        min_length = sentence_lengths.min()
        self.log('Minimal sentence length:', min_length)
        max_length = sentence_lengths.max()
        self.log('Maximal sentence length:', max_length)
        #boxplot
        fig, ax = plt.subplots()
        ax.boxplot(sentence_lengths.values, whis=1.5)
        ax.set_ylim([0, 45])
        ax.set_title('Distribution of Sentence Length')
        ax.set_xlabel('Sentence')
        ax.set_ylabel('Length in Words')
        plt.savefig('descriptive_statistic/plots/sentenceLengthBP.png')
        plt.show()
        #create histogram
        fig, ax = plt.subplots()
        ax.set_title('Sentence Length')
        ax.hist(sentence_lengths.values, bins=42)
        ax.set_xlim([0, 44])
        ax.set_xlabel('Length of Sentence')
        ax.set_ylabel('Number of Sentences')
        plt.savefig('descriptive_statistic/plots/sentenceLengthHist.png')
        plt.show()
        sentence_counts = sentence_lengths.value_counts().sort_index()
        table = pd.DataFrame({
            'Number of sentences': sentence_counts.index,
            'Number of words': sentence_counts.values
        })
        table.to_csv('descriptive_statistic/tables/sentence_length.csv', index=False)

    def count_usuable_abstracts(self):
        """count database entries with a abstract"""
        cur = self.conn.cursor()
        cur.execute("SELECT COUNT(*) FROM citation WHERE abstract IS NULL")
        num_null = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM citation WHERE abstract IS NOT NULL")
        num_not_null = cur.fetchone()[0]
        print(f"Column 'abstract' has {num_null} null values and {num_not_null} non-null values.")
        
    def run(self):
        self.analyze_paragraphs_per_paper()
        self.analyze_sentences_per_paragraph()
        self.analyze_sentence_length()
        self.analyze_citations_per_sentence()
        self.conn.close()

if __name__ == "__main__":
    run = descriptiveStatistics('dataset/database/dataset.db')
    run.run()

