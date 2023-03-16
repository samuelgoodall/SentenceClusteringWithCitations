from sklearn.metrics import silhouette_score
from soyclustering import SphericalKMeans
from numpy import argmax, asarray, log
from scipy.sparse import csr_matrix
from sklearn.mixture import GaussianMixture


class AutomaticClusterFinder:

    def __init__(self, model: str, data: list, verbose: int = 0):
        """Creates an AutomaticClusterFinder object which tries to find the best number of cluster for the data.
        If the model is skmeans the silhouette criterion is used with spherical kmeans.
        If the model is gmm the bic criterion is used with a gmm.

                   Parameters
                   ----------
                   model : {'skmeans', 'gmm'}
                       Decides wether the silhouette criterion with spherical kmeans is used or
                       the bic criterion with gmm

                   data : list
                        Data for which the number of clusters should be estimated

                   verbose : int, default 0
                        switch verbose mode on/off
        """
        self.model = model
        self.data = data
        self.verbose = verbose

    def find_best_k(self, max_range: int) -> int:
        """Estimates the best number of clusters based on the selected model

                   Parameters
                   ----------
                   max_range : int
                       Maximal number of clusters for the model to test on the data

                   Returns
                   -------
                   best_k : int
                       the best number of clusters. If a wrong model is selected returns -1
               """
        if self.model == "skmeans":
            return self._find_with_silhouette(max_range)
        elif self.model == "gmm":
            return self._find_with_bic(max_range)
        else:
            return -1

    def _find_with_silhouette(self, max_range: int) -> int:
        """Private method to use silhouette criterion with the Spherical Kmeans model

                   Parameters
                   ----------
                   max_range : int
                       Maximal number of clusters for the model to test on the data

                   Returns
                   -------
                   best_k : int
                       the best number of clusters.
               """
        silhouette_avg = []
        for num_clusters in list(range(2, max_range)):
            skmeans = SphericalKMeans(n_clusters=num_clusters, init="k-means++")
            skmeans.fit_predict(csr_matrix(self.data))
            score = silhouette_score(self.data, skmeans.labels_)
            if self.verbose:
                print("Silhouette score for number of cluster(s) {}: {}".format(num_clusters, score))
                print("-" * 100)
            silhouette_avg.append(score)
        best_score = argmax(silhouette_avg) + 2
        return best_score

    def _find_with_bic(self, max_range: int):
        """Private method to use bic criterion with the gmm model

                           Parameters
                           ----------
                           max_range : int
                               Maximal number of clusters for the model to test on the data

                           Returns
                           -------
                           best_k : int
                               the best number of clusters.
                       """
        gm_bic = []
        gm_score = []
        for i in range(2, max_range):
            gm = GaussianMixture(n_components=i, init_params="k-means++").fit(self.data)
            if self.verbose:
                print("BIC for number of cluster(s) {}: {}".format(i, gm.bic(asarray(self.data))))
                print("Log-likelihood score for number of cluster(s) {}: {}".format(i, gm.score(self.data)))
                print("-" * 100)
            gm_bic.append(-gm.bic(asarray(self.data)))
            gm_score.append(gm.score(self.data))

        best_score = argmax(gm_bic) + 2
        return best_score
