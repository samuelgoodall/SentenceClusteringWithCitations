import os
import shutil
import zipfile
from pathlib import Path

import requests
from tqdm import tqdm


from experiments.embedding_methods.glove_embedding import GloveEmbedding


def download_with_progress_bar(URL,output_path):
    with requests.get(URL, stream=True) as r:
        output_path = os.path.join(output_path,os.path.basename(r.url))
        if not os.path.isfile(output_path):
            total_length = int(r.headers.get("Content-Length"))
            # implement progress bar via tqdm
            with tqdm.wrapattr(r.raw, "read", total=total_length, desc="") as raw:
                # save the output to a file
                with open(f"{output_path}", 'wb') as output:
                    shutil.copyfileobj(raw, output)
    return output_path
def main():
    print("downloading glove_embeddings")
    URL = "https://nlp.stanford.edu/data/glove.840B.300d.zip"
    output_path = os.path.abspath("experiments/embedding_methods/embeddings/glove")
    if not os.path.isdir(output_path):
        Path(output_path).mkdir(exist_ok=True)
    file_path = download_with_progress_bar(URL,output_path=output_path)
    print("unzip glove embeddings")
    if not os.path.isfile(os.path.join(output_path, "glove.840B.300d.txt")):
        with zipfile.ZipFile(file_path, "r") as zip_ref:
            zip_ref.extractall(output_path)

    print("create KeyedVectors from GLoveEmbeddings")
    glove_embeddings_path = "experiments/embedding_methods/embeddings/glove/glove.840B.300d.txt"
    embedding = GloveEmbedding(300, glove_embeddings_path)

if __name__ == "__main__":
    print("hello world!")
    main()

