from clustering_interface import ClusteringInterface
from soyclustering import SphericalKMeans
from scipy.sparse import csr_matrix
from sklearn.metrics import silhouette_score
from numpy import argmax


class SphericalKMeansClustering(ClusteringInterface):

    def __init__(
            self,
            num_clusters: int = None,
            max_range: int = 20,
            init: str = "k-means++",
            sparsity: str = None,
            max_iter: int = 10,
            tol: float = 1e-4,
            verbose: int = 0,
            random_state=None,
            max_similar: float = 0.5,
            alpha: float = 3.0,
            radius: float = 10.0,
            epsilon: float = 5.0,
            minimum_df_factor: float = 0.01,
    ):
        """ Creates a SphericalKmeansClustering object with the according parameters. These attributes are used for the
        creation of the SphericalKmeans object. If no cluster number is passed we use silhouette criterion to calculate the optimal number

                Parameters
                ----------

                num_clusters : int,
                    The number of clusters to form as well as the number of centroids to generate.

                max_range : int, default: 20
                    The range of cluster numbers to evaluate the silhouette criterion for determining
                    the optimal cluster number if no cluster number is given at initialization

                init : str or numpy.ndarray, default: 'similar_cut'
                    One of ['similar_cut', 'k-means++', 'random'] or an numpy.ndarray
                    Method for initialization,
                    - 'similar_cut'
                    It is an k-means initialization method for high-dimensional vector space + Cosine.
                    See `Improving spherical k-means for document clustering (Kim et al., 2020)` for detail.
                    - 'k-means++'
                    It selects initial cluster centers for k-means clustering in a smart way to speed up convergence.
                    See https://en.wikipedia.org/wiki/K-means%2B%2B for detail.
                    - 'random'
                    choose k observations (rows) at random from data for the initial centroids.
                    - If an ndarray is passed, it should be of shape (n_clusters, n_features) and gives the initial centers.

                sparsity: str or None, default: None
                    One of ['sculley', 'minimum_df', None]
                    Method for preserving sparsity of centroids.
                    'sculley': L1 ball projection method.
                        Reference: David Sculley. Web-scale k-means clustering.
                        In Proceedings of international conference on World wide web,2010.
                        It requires two parameters `radius` and `epsilon`.
                        `radius`: default 10
                        `epsilon`: default 5
                    'minium_df': Pruning method. It drops elements to zero which lower
                        than beta / |DF(C)|. DF(C) is the document number of a cluster and
                        beta is constant parameter.
                        It requires one parameter `minimum_df_factor` a.k.a beta
                        `minimum_df_factor`: default 0.01

                max_iter : int, default: 10
                    Maximum number of iterations of the k-means algorithm for a single run.
                    It does not need large number. k-means algorithms converge fast.

                tol : float, default: 1e-4
                    Relative tolerance with regards to inertia to declare convergence

                verbose : int, default 0
                    Verbosity mode.

                random_state : int, RandomState instance or None, optional, default: None
                    If int, random_state is the seed used by the random number generator;
                    If RandomState instance, random_state is the random number generator;
                    If None, the random number generator is the RandomState instance used
                    by `numpy.random`.

                max_similar: float, default: 0.5
                    'similar_cut initializer' argument. The initializer select a point randomly,
                    and then remove points within distance <= `max_similar` from candidates of
                    next centroid. It works only when you set `init`='similar_cut'.

                alpha: float, default: 3.0
                    'similar_cut initializer' argument. |candidates of initial centroids| / `n_clusters`
                    It works only when you set `init`='similar_cut'.
                    `alpha` must be larger than 1.0

                radius: float, default: 10.0
                    'sculley L1 projection' argument. It works only when you set `sparsity`='sculley'

                epsilon: float, default: 5.0
                    'sculley L1 projection' argument. It works only when you set `sparsity`='sculley'

                minimum_df_factor: float, default: 0.01
                    'minimum df L1 projection' argument. It works only when you set `sparsity`='minimum_df'
                    `minimum_df_factor` must be real number between (0, 1)
                """
        self.num_clusters = num_clusters
        self.max_range = max_range
        self.max_iter = max_iter
        self.sparsity = sparsity
        self.init = init
        self.tol = tol
        self.verbose = verbose
        self.random_state = random_state
        self.max_similar = max_similar
        self.alpha = alpha
        self.radius = radius
        self.epsilon = epsilon
        self.min_df_factor = minimum_df_factor

    def cluster_sentences(self, sentences: list):
        """Creates a soyclustering.SphericalKmeans object with the attributes of the SphericalKmeansClustering class,
        transforms the input sentences to a csr matrix and retruns the calculated labels.

            Parameters
            ----------
            sentences : list
                Input data for which the cluster labels should be predicted via a GMM

            Returns
            -------
            labels : list
                a list with the corresponding predicted labels for the input data
        """
        num_samples = len(sentences)
        if self.num_clusters is None:
            self.num_clusters = self._find_k_with_silhouette(sentences)

        if num_samples == 1:
            return [0]
        elif num_samples < self.num_clusters:
            spherical_kmeans = SphericalKMeans(
                n_clusters=num_samples,
                max_iter=self.max_iter,
                sparsity=self.sparsity,
                init=self.init,
                tol=self.tol,
                verbose=self.verbose,
                random_state=self.random_state,
                max_similar=self.max_similar,
                alpha=self.alpha,
                radius=self.radius,
                epsilon=self.epsilon,
                minimum_df_factor=self.min_df_factor,
            )
        else:
            spherical_kmeans = SphericalKMeans(
                n_clusters=self.num_clusters,
                max_iter=self.max_iter,
                sparsity=self.sparsity,
                init=self.init,
                tol=self.tol,
                verbose=self.verbose,
                random_state=self.random_state,
                max_similar=self.max_similar,
                alpha=self.alpha,
                radius=self.radius,
                epsilon=self.epsilon,
                minimum_df_factor=self.min_df_factor,
            )
        input_to_csr = csr_matrix(sentences)
        spherical_kmeans.fit(input_to_csr)
        return spherical_kmeans.labels_

    def return_hyper_params(self):
        """Returns the attributes of the GMMClustering class, which are also the hyperparameter of the created GMM model
        in the cluster_sentence method.

        Returns
        -------
        hyper_params : dict
            a dictionary with the name of the hyperparameter and the corresponding value
        """
        hyper_params = {
            "num_cluster": self.num_clusters,
            "max_range": self.max_range,
            "max_iter": self.max_iter,
            "sparsity": self.sparsity,
            "init": self.init,
            "tol": self.tol,
            "verbose": self.verbose,
            "max_similar": self.max_similar,
            "alpha": self.alpha,
            "radius": self.radius,
            "epsilon": self.epsilon,
            "minimum_df_factor": self.min_df_factor,
        }
        return hyper_params

    def _find_k_with_silhouette(self, sentences: list) -> int:
        """Private method to use silhouette criterion with the Spherical Kmeans model
                   Parameter
                   --------
                   sentences : list
                       data to evaluate silhouette criterion

                   Returns
                   -------
                   best_k : int
                       the best number of clusters.
               """
        silhouette_avg = []
        for num_clusters in list(range(2, self.max_range)):
            skmeans = SphericalKMeans(
                n_clusters=num_clusters,
                max_iter=self.max_iter,
                sparsity=self.sparsity,
                init=self.init,
                tol=self.tol,
                verbose=0,
                random_state=self.random_state,
                max_similar=self.max_similar,
                alpha=self.alpha,
                radius=self.radius,
                epsilon=self.epsilon,
                minimum_df_factor=self.min_df_factor,
            )
            skmeans.fit_predict(csr_matrix(sentences))
            score = silhouette_score(sentences, skmeans.labels_, metric='cosine')
            if self.verbose:
                print("Silhouette score for number of cluster(s) {}: {}".format(num_clusters, score))
                print("-" * 100)
            silhouette_avg.append(score)
        best_score = argmax(silhouette_avg) + 2
        print(f"Selected optimal number of clusters: {best_score} ")
        return best_score
