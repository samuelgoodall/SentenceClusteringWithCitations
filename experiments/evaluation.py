import os
from datetime import datetime
import json
import time
from enum import Enum

import numpy as np
from sklearn import metrics
from tqdm import tqdm

from dataset.customDataloader import get_dataloader
from experiments.clustering_methods.clustering_interface import ClusteringInterface
from experiments.clustering_methods.db_scan_clustering import DBScanClustering
from experiments.embedding_methods.embedding_interface import EmbeddingInterface
from experiments.embedding_methods.bert_embedding import BertTransformerEmbedding


class SentenceCitationFusingMethod(Enum):
    Concatenation = 1
    Averaging = 2


def calculate_correct_labels(labels: list[int]):
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


def get_evaluation_metrics(labels: list[int], labels_predicted: list[int]):
    """computes all the evaluation metrics"""
    ari = metrics.adjusted_rand_score(labels, labels_predicted)
    nmi = metrics.normalized_mutual_info_score(labels, labels_predicted)
    fms = metrics.fowlkes_mallows_score(labels, labels_predicted)

    return ari, nmi, fms


def save_result(embedding_hyper_params: dict, clustering_hyper_params: dict, running_time: float):
    """saves results of experiment as json"""
    result = dict()
    result["time_stamp"] = datetime.now().strftime("%d/%m/%Y, %H:%M:%S")
    result["running_time"] = running_time
    result["embedding_hyper_params"] = embedding_hyper_params
    result["clustering_hyper_params"] = clustering_hyper_params
    output_name = 'results.json'
    if not os.path.isfile(output_name):
        overall_results = []
        with open(output_name, 'w') as f:
            json.dump(overall_results, f, indent=4)
    with open(output_name) as f:
        overall_results = json.load(f)
        overall_results.append(result)
    with open(output_name, "w") as f:
        json.dump(overall_results, f, indent=4)


def evaluate(embedding: EmbeddingInterface, clustering: ClusteringInterface):
    # is one at the moment makes iterating easier, batch size of 200 would save some seconds of execute
    batch_size = 1
    dataloader = get_dataloader(batch_size, shuffle=False)
    count = 0
    start = time.time()
    eval_metrics = np.asarray((0.0, 0.0, 0.0))

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
        current_metrics = get_evaluation_metrics(labels, labels_predicted)
        eval_metrics += np.asarray(current_metrics) / len(dataloader)
        count += 1

    runtime = time.time() - start
    embedding_hyper_params = embedding.return_hyper_params()
    clustering_hyper_params = clustering.return_hyper_params()
    save_result(embedding_hyper_params=embedding_hyper_params, clustering_hyper_params=clustering_hyper_params,
                running_time=runtime)


def main():
    embedding = BertTransformerEmbedding("bert-base-uncased")
    clustering = DBScanClustering(eps=1.5, min_samples=1, metric="euclidean")
    evaluate(embedding, clustering)


if __name__ == "__main__":
    main()
