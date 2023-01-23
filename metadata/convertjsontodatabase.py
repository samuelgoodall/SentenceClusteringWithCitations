import json
import os
import sqlite3
from sqlite3 import Error
from zipfile import ZipFile

from tqdm import tqdm


def create_connection(db_file):
    """ create a database connection to a SQLite database """
    try:
        conn = sqlite3.connect(db_file)
        print(sqlite3.version)
        return conn
    except Error as e:
        print(e)

def create_table(conn,create_table_sql):
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except Error as e:
        print(e)

def create_meta_data_entry(conn, meta_data_entry):
    """
    Create a new meta_data_entry
    :param conn:
    :param meta_data_entry:
    :return:
    """

    sql = ''' INSERT INTO meta_data_entrys(entry_id,paper_id,submitter,authors,title,comments,journal_ref,doi,report_no,categories,license,abstract,update_date)
              VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?) '''
    cur = conn.cursor()
    cur.execute(sql, meta_data_entry)
    conn.commit()

    return cur.lastrowid

def write_to_meta_database(count:int, conn):
    """
    writes metadata to meta database
    :param conn: conection for to the database
    :param count: number of items in json in order to display tqdm
    :return:
    """
    print("openingFile")
    with tqdm(total=count) as pbar:
        with open(file_path) as f:
            for line in tqdm(f):
                j_content = json.loads(line)
                pbar.update(1)
                create_meta_data_entry(conn, meta_data_entry=(None,
                j_content["id"], j_content["submitter"], j_content["authors"], j_content["title"],
                j_content["comments"], j_content["journal-ref"], j_content["doi"], j_content["report-no"],
                j_content["categories"], j_content["license"], j_content["abstract"], j_content["update_date"]))

def count_entries_in_json(file_path):
    """
    counts the entries in json
    :param file_path: path to json
    :return:
    """
    with open(file_path, 'r') as fp:
        for count, line in enumerate(fp):
            pass
    return count

def unzip_meta_dataset(file_path):
    """
    unzips the farxiv metadata dataset zip
    :param file_path:
    :return:
    """
    print("starting extraction")
    with ZipFile(file_path, 'r') as file:
        file.extractall()
    print("finished extraction")


if __name__ == '__main__':

    file_path = "./arxiv-metadata-oai-snapshot.json"
    database_name = r"database.db"
    files_in_folder = os.listdir()

    dataset_zipped_file_name = "archive.zip"
    unzip_meta_dataset(dataset_zipped_file_name)
    
    conn = create_connection(database_name)
    sql_create_projects_table = """ CREATE TABLE IF NOT EXISTS meta_data_entrys (
                                            entry_id INTEGER PRIMARY KEY,
                                            paper_id text ,
                                            submitter text ,
                                            authors text ,
                                            title text ,
                                            comments text ,
                                            journal_ref text,
                                            doi text,
                                            report_no text,
                                            categories text,
                                            license text,
                                            abstract text,
                                            update_date text
                                        ); """

    create_table(conn,sql_create_projects_table)

    count = count_entries_in_json(file_path)

    write_to_meta_database(count,conn)



