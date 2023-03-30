import kneed

from sklearn.cluster import DBSCAN
from scipy.spatial import distance

from experiments.clustering_methods.clustering_interface import ClusteringInterface


class DBScanClustering(ClusteringInterface):

    def __init__(self, eps: float = None, min_samples: int = 1, metric: str = "cosine"):
        self.eps = eps
        self.min_samples = min_samples
        self.metric = metric

    def cluster_sentences(self, sentences: list):
        """clusters sentences using db_scan"""
        if self.eps is None:
            self.eps = self.find_best_eps(sentences)
        db = DBSCAN(eps=self.eps, min_samples=self.min_samples, metric=self.metric).fit(sentences)
        labels_predicted = db.labels_
        return labels_predicted

    def return_hyper_params(self):
        """returns the hyper params of the clustering algorithm"""
        hyper_params = {"eps": self.eps, "min_samples": self.min_samples, "metric": self.metric}
        return hyper_params

    def find_best_eps(self, sentences):
        distance_list = []
        indexes = range(len(sentences))

        if self.metric == "euclidean":
            dist = distance.euclidean
        elif self.metric == "cosine":
            dist = distance.cosine
        else:
            return -1
        for i in range(len(sentences)):
            sum_dist = 0
            for k in range(len(sentences)):
                if i != k:
                    sum_dist += dist(sentences[i], sentences[k])
            distance_list.append(sum_dist/(len(sentences)-1))
        distance_list.sort()
        elbow_locator = kneed.KneeLocator(x=range(len(sentences)), y=distance_list,
                                          curve="convex", direction="increasing", interp_method="interp1d",
                                          online=True, S=1)
        optimal_eps = distance_list[elbow_locator.elbow]
        print(f"Selected optimal eps value: {optimal_eps} ")
        return optimal_eps
