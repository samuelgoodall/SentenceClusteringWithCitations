import json
import os
import time
from datetime import datetime
from enum import Enum
import statistics
import numpy as np
from sklearn import metrics
from torch.utils.data import DataLoader
from tqdm import tqdm

from dataset.customDataloader import get_dataloader, get_train_test_validation_dataloader
from dataset.customDataloaderPrecomputedEmbeddings import ArxivDatasetPrecomputedEmbeddings
from experiments.clustering_methods.clustering_interface import ClusteringInterface
from experiments.clustering_methods.db_scan_clustering import DBScanClustering
from experiments.clustering_methods.spherical_kmeans_clustering import SphericalKMeansClustering
from experiments.embedding_methods.embedding_interface import \
    EmbeddingInterface, SentenceCitationFusingMethod
from experiments.embedding_methods.fasttext_embedding import FastTextEmbedding
from experiments.embedding_methods.glove_embedding import GloveEmbedding


def calculate_correct_labels(labels: list[int]) -> None:
    """
    calculates the correct labels and swaps them in place
    this is necessary to make evaluation easier otherwise the clusterlabels would just be the database indexes

    Parameters
    ----------
    labels:list[int]
        list of labels, the ith position in the list corresponds to the ith example that is to be clustered

    Returns
    -------
    None
        this method performs an inplace operation so the return is None as is convention
    """
    label_cluster_index = 0
    label_map = {}
    for label_index, label in enumerate(labels):
        if label not in label_map:
            label_map[label] = label_cluster_index
            label_cluster_index += 1
        labels[label_index] = label_map[label]
    return None

def get_evaluation_metrics(labels: list[int], labels_predicted: list[int]) -> dict:
    """
    computes all the evaluation metrics

    Parameters
    ----------
    labels : list[int]
        a list of the true labels
    labels_predicted: list[int]
        a list of the predicted labels

    Returns
    -------
    dict
       dict with the evaluation Metrics used
    """
    ari = metrics.adjusted_rand_score(labels, labels_predicted)
    nmi = metrics.normalized_mutual_info_score(labels, labels_predicted)
    fms = metrics.fowlkes_mallows_score(labels, labels_predicted)
    return {"ARI": ari, "NMI": nmi, "FMS": fms}


def save_result(embedding: EmbeddingInterface, clustering: ClusteringInterface, running_time: float,
                evaluation_metrics: dict, use_citation: bool):
    """
    saves results of experiment as json

    Parameters
    ----------
    embedding : EmbeddingInterface
        the embedding class that is responsible for embedding the sentences
    clustering : ClusteringInterface
        the clustering class that is responsible for clustering the sentences
    running_time: float
        the running time of the evaluation
    evaluation_metrics:dict
        the evalutation metrics that are computed during evaluation
    """
    embedding_hyper_params = embedding.return_hyper_params()
    clustering_hyper_params = clustering.return_hyper_params()
    eval_metrics_result = {"ARI": 0.0, "NMI": 0.0, "FMS": 0.0}
    for key in eval_metrics_result.keys():
        eval_metrics_result[key] = statistics.mean(evaluation_metrics[key])
    result = dict()
    result["time_stamp"] = datetime.now().strftime("%d/%m/%Y, %H:%M:%S")
    result["running_time"] = running_time
    result["with_citation_information"] = use_citation
    result["evalution_metrics"] = eval_metrics_result
    result["embedding_type"] = type(embedding).__name__
    result["clustering_type"] = type(clustering).__name__
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


def evaluate(embedding: EmbeddingInterface, clustering: ClusteringInterface, dataloader: DataLoader = None,
             use_citation: bool = True):
    """
    evaluates the dataset given as dataloader
    saves the evaluation metrics as results.json in current directory

    Parameters
    ----------
    embedding : EmbeddingInterface
        the embedding class that is responsible for embedding the sentences
    clustering : ClusteringInterface
        the clustering class that is responsible for clustering the sentences
    dataloader: DataLoader
        the dataloader that is used to iterate over the dataset
    use_citation: bool
        flag to set to evaluate with or without embedding the citation(the title)
    """

    count = 0
    start = time.time()
    eval_metrics = {"ARI": [], "NMI": [], "FMS": []}
    for i, data in enumerate(tqdm(dataloader)):
        sentences, labels = data[0]
        calculate_correct_labels(labels)
        bag_of_sentences = embedding.embed_sentences(sentences, use_citation=use_citation)
        # cluster & evaluate the stuff:
        labels_predicted = clustering.cluster_sentences(bag_of_sentences)
        current_metrics = get_evaluation_metrics(labels, labels_predicted)
        # update eval_metrics
        for key in eval_metrics.keys():
            eval_metrics[key].append(current_metrics[key])

        count += 1

    runtime = time.time() - start


    save_result(embedding=embedding, clustering=clustering,
                running_time=runtime, evaluation_metrics=eval_metrics, use_citation=use_citation)


def evaluate_with_precomputed_embeddings(embedding: EmbeddingInterface, clustering: ClusteringInterface,
                                         dataloader: DataLoader = None, use_citation: bool = True):
    """
    evaluates the dataset given as dataloader
    uses dataset where embeddings have been precomputed
    saves the evaluation metrics as results.json in current directory

    Parameters
    ----------
    clustering : ClusteringInterface
        the clustering class that is responsible for clustering the sentences
    embedding : EmbeddingInterface
        the embedding class that is responsible for embedding the sentences
    dataloader: DataLoader
        the dataloader that is used to iterate over the dataset
    use_citation: bool
        flag to set to evaluate with or without embedding the citation(the title)
    """

    count = 0
    start = time.time()
    eval_metrics = {"ARI": [], "NMI": [], "FMS": []}
    for i, data in enumerate(tqdm(dataloader)):
        sentences, labels = data[0]
        bag_of_sentences = []
        calculate_correct_labels(labels)
        for sentence_index, sentence in enumerate(sentences):
            sentence_embedding = sentence.sentence_embedded
            citation_embeddings = []
            if use_citation:
                for citation in sentence.citations:
                    current_citation_embedding = citation.citation_title_embedded
                    citation_embeddings.append(current_citation_embedding)
                overall_embedding = EmbeddingInterface.fuse_sentence_and_citation_embedding(sentence_embedding=sentence_embedding,
                                                                         citation_embeddings=citation_embeddings,
                                                                         sentence_citation_fusing_method=SentenceCitationFusingMethod.Averaging)
            else:
                overall_embedding = sentence_embedding
            bag_of_sentences.append(overall_embedding)
        # cluster & evaluate the stuff:
        labels_predicted = clustering.cluster_sentences(bag_of_sentences)
        # print("LABEls:", labels)
        # print("labels_predicted", labels_predicted)
        current_metrics = get_evaluation_metrics(labels, labels_predicted)

        # update eval_metrics
        for key in eval_metrics.keys():
            eval_metrics[key].append(current_metrics[key])

        count += 1

    runtime = time.time() - start
    save_result(embedding=embedding, clustering=clustering,
                running_time=runtime, evaluation_metrics=eval_metrics, use_citation=use_citation)
