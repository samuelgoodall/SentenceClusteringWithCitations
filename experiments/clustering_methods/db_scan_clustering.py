import json

from sklearn.cluster import DBSCAN

from experiments.clustering_methods.clustering_interface import ClusteringInterface


class DBScanClustering(ClusteringInterface):

    def __init__(self, eps: float, min_samples: int, metric: str):
        self.eps = eps
        self.min_samples = min_samples
        self.metric = metric

    def cluster_sentences(self, sentences: list):
        """clusters sentences using db_scan"""
        db = DBSCAN(eps=self.eps, min_samples=self.min_samples, metric=self.metric).fit(sentences)
        labels_predicted = db.labels_
        return labels_predicted

    def return_hyper_params(self):
        """returns the hyper params of the clustering algorithm"""
        hyper_params = {"eps": self.eps, "min_samples": self.min_samples, "metric": self.metric}
        return hyper_params
