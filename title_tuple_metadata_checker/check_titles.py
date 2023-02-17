import pandas as pd

from title_tuple_metadata_checker import count_usable_citations


conn = count_usable_citations.create_connection(r"/home/esteli/Documents/Data_Science/database.db")
paper_count = 0
title_matches = 0
csv_dir = ["/home/esteli/Documents/Data_Science/data0.csv", "/home/esteli/Documents/Data_Science/data1.csv",
           "/home/esteli/Documents/Data_Science/data2.csv", "/home/esteli/Documents/Data_Science/data3.csv",
           "/home/esteli/Documents/Data_Science/data4.csv", "/home/esteli/Documents/Data_Science/data5.csv",
           "/home/esteli/Documents/Data_Science/data6.csv", "/home/esteli/Documents/Data_Science/data7.csv"]
for csv in csv_dir:
    df = pd.read_csv(csv)
    titles = df["citation_titles"]

    for item in titles:
        item = item.strip("['']")
        database_title_match = count_usable_citations.check_if_in_database(item, conn)
        paper_count += 1
        if database_title_match:
            title_matches += 1
    print("total papers: ", paper_count, "; titles with matches", title_matches)

#add counter for papers without an abstract

