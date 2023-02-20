import time

import pandas as pd


def main():
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
