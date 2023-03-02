import sqlite3
import time

from torch.utils.data import Dataset, DataLoader

from database.database import SQAlchemyDatabase, Paper


class ArxivDataset(Dataset):
    """
    Map Style Dataset for our usecase
    """
    def __init__(self, db_path: str):
        self.db_path = db_path
        database = SQAlchemyDatabase(db_path)
        session = database.session()
        engine = database.engine
        self.length = session.query(Paper).count()
        session.close()
        engine.dispose()

    def __len__(self):
        return self.length

    def __getitem__(self, idx):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        sql_script = """
                        Select paragraph.id, sentence.content,c.title,c.abstract
                                from paragraph
                                    INNER JOIN sentence 
                                        ON sentence.paragraph_id = paragraph.id
                                        AND paper_id = ?
                                        INNER JOIN sentence_citation_relation ON
                                            sentence.id = sentence_citation_relation.sentence_id
                                                INNER JOIN citation c on c.id = sentence_citation_relation.citation_id
        """
        cursor.execute(sql_script, (idx+1,))
        rows = cursor.fetchall()
        sentences = []
        labels = []
        for item in rows:
            sentence_citation = {
                "sentence": item[1],
                "citation_title": item[2],
                "citation_abstract": item[3] if (item[3] is not None) else "",
            }
            sentences.append(sentence_citation)
            labels.append(item[0])
        return sentences, labels

def custom_collate(batch):
    return batch

def get_dataloader(batch_size = 20,shuffle=False):
    dataset = ArxivDataset("database/dataset.db")
    train_dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=shuffle, collate_fn=custom_collate)
    return train_dataloader

if __name__ == "__main__":
    dataset = ArxivDataset("../database/dataset.db")
    train_dataloader = DataLoader(dataset, batch_size=200, shuffle=True,collate_fn=custom_collate)

    start = time.time()
    example = next(iter(train_dataloader))
    end = time.time()

    print("seconds",end - start)