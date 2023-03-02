import time
from enum import Enum

import numpy as np
from sklearn import metrics
from tqdm import tqdm

from dataset.customDataloader import get_dataloader
from experiments.clustering_methods.db_scan_clustering import DBScanClustering
from experiments.embedding_methods.glove_embedding import GloveEmbedding

class SentenceCitationFusingMethod(Enum):
    Concatenation = 1
    Averaging = 2

def calculate_correct_labels(labels:list[int]):
    """
    calculates the correct labels and swaps them in place
    this is necessary to make evaluation easier otherwise the clusterlabels would just be the database indexes
    ______
    labels:list[int]
        list of labels, the ith position in the list corresponds to the ith example that is to be clustered
    """
    label_cluster_index = 0
    label_map = {}
    for label_index, label in enumerate(labels):
        if label not in label_map:
            label_map[label] = label_cluster_index
            label_cluster_index += 1
        labels[label_index] = label_map[label]
    return None

def fuse_sentence_and_citation_embedding(sentence_embedding, sentence_citation_embedding,
                                         sentence_citation_fusing_method: SentenceCitationFusingMethod):
    """
    sentence_citation_fusing_method: SentenceCitationPoolingMethod
        method to be used for fusing sentence and citation concat or average
    """
    if sentence_citation_fusing_method == SentenceCitationFusingMethod.Averaging:
        return (sentence_embedding + sentence_citation_embedding) / 2
    if sentence_citation_fusing_method == SentenceCitationFusingMethod.Concatenation:
        return np.concatenate((sentence_embedding, sentence_citation_embedding), axis=None)
def main():

    # is one at the moment makes iterating easier, batch size of 200 would save some sekonds of execute
    batch_size = 1
    dataloader = get_dataloader(batch_size,shuffle=False)
    count = 0
    start = time.time()

    glove_embeddings_path = "../embeddings/glove/glove.840B.300d.txt"
    embedding = GloveEmbedding(300,glove_embeddings_path)
    clustering = DBScanClustering(eps=1.5, min_samples=1, metric="euclidean")

    #Adjusted Rand index as performance measure of the clustering
    ARI = 0


    for i, data in enumerate(tqdm(dataloader)):
        sentences, labels = data[0]
        bag_of_sentences = []
        calculate_correct_labels(labels)
        for sentence_index, sentence in enumerate(sentences):
            sentence_embedding = embedding.embed_sentence(sentence["sentence"])
            sentence_citation_embedding = embedding.embed_sentence(sentence["citation_title"])
            overall_embedding = fuse_sentence_and_citation_embedding(sentence_embedding,
                                                                     sentence_citation_embedding,
                                                                     SentenceCitationFusingMethod.Averaging)
            bag_of_sentences.append(overall_embedding)

        # cluster & evaluate the stuff:

        labels_predicted = clustering.cluster_sentences(bag_of_sentences)
        current_ari = metrics.adjusted_rand_score(labels, labels_predicted)
        ARI += current_ari/len(dataloader)
        count += 1

    end = time.time()
    print("count", count)
    print("time", -start + end)
    print("ARI:", ARI)

if __name__ == "__main__":
    main()