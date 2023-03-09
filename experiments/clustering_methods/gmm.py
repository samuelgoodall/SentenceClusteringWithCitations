from experiments.clustering_methods.clustering_interface import ClusteringInterface
from sklearn.mixture import GaussianMixture
class GMMClustering(ClusteringInterface):

    def __init__(self):
        pass

    def cluster_sentences(self, sentences: list):
        """clusters sentences using gmm"""
        pass


    def return_hyper_params(self):
        """returns the hyper params of the clustering algorithm"""
        pass