"""script for counting the citations that are in the meta_database.
They are given by name and author tuples in a json file"""
import argparse
import sqlite3

import ijson
from tqdm import tqdm


def create_connection(db_file):
    """ create a database connection to a SQLite database """
    try:
        conn = sqlite3.connect(db_file)
        print(sqlite3.version)
        return conn
    except sqlite3.Error as e:
        print(e)


def check_if_in_database(title, conn):
    """
    counts the entries in json
    :title check if theres an entry to the given title in the databse
    :conn connection to database
    :return:
    """
    sql = ''' Select * FROM meta_data_entrys WHERE title=?'''
    cur = conn.cursor()
    result = cur.execute(sql, (title,))
    result = result.fetchall()
    return result


def count_entries_in_json(file_path):
    """
    counts the entries in json
    :param file_path: path to json
    :return:
    """
    count = 0
    with open(file_path, "rb") as f:
        for record in ijson.items(f, "item", multiple_values=True):
            count += 1
    return count


def count_entries_that_are_in_database(count, conn, file_path):
    """
        counts the entries in json
        :param conn: conection for to the database
        :param count: number of items in json in order to display tqdm
        :return: int number of usable citations
    """
    print("starting to count entries that are in database!")
    incount = 0
    with tqdm(total=count) as pbar:
        with open(file_path, "rb") as f:
            for record in tqdm(ijson.items(f, "item", multiple_values=True)):
                title = record[0][1]
                indatabase = check_if_in_database(title, conn)
                if (len(indatabase) >= 1):
                    incount += 1
                pbar.update(1)
    return incount


def process_arguements():
    # Create the parser
    parser = argparse.ArgumentParser()  # Add an argument
    parser.add_argument('--db_path', type=str, required=True)  # Parse the argument
    parser.add_argument('--json_file', type=str, required=True)  # Parse the argument
    args = parser.parse_args()  # Print "Hello" + the user input argument
    return args.db_path, args.json_file


def main() -> None:
    print("starting metadata cheking")
    database_name, filepath = process_arguements()
    print(database_name, filepath)
    count = count_entries_in_json(filepath)
    print("Number of Items", count)
    conn = create_connection(db_file=database_name)
    in_count = count_entries_that_are_in_database(count, conn, filepath)
    print("COUNT:", count)
    print("INCOUNT", in_count)
    print("inRatio", in_count / count)
    output = open("countingOutput", "a")
    output.write(
        "OverallCount:" + str(count) + ",InCount:" + str(in_count) + ",inRatio:" + str(in_count / count) + "\n")

if __name__ == "__main__":
    main()
