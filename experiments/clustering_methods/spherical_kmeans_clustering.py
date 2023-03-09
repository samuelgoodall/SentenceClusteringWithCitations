from clustering_interface import ClusteringInterface
from soyclustering import SphericalKMeans
from scipy.sparse import csr_matrix


class SphericalKMeansClustering(ClusteringInterface):
    """n_clusters : int, optional, default: 8
            The number of clusters to form as well as the number of centroids to generate.
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
        debug_directory: str, default: None
            When debug_directory is not None, model save three informations.
            First one is logs. It contains iteration time, loss, and sparsity.
            Second one is temporal cluster labels for all iterations. Third one
            is temporal cluster centroid vector for all iterations.
        algorithm : str, default None
            Computation algorithm.
            Ignored
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

    def __init__(
        self,
        num_clusters: int,
        init: str = "k-means++",
        sparsity: str = None,
        max_iter: int = 15,
        tol: float = 1e-4,
        verbose: int = 0,
        max_similar: float = 0.5,
        alpha: float = 3.0,
        radius: float = 10.0,
        epsilon: float = 5.0,
        minimum_df_factor: float = 0.01,
    ):
        self.num_clusters = num_clusters
        self.max_iter = max_iter
        self.sparsity = sparsity
        self.init = init
        self.tol = tol
        self.verbose = verbose
        self.max_similar = max_similar
        self.alpha = alpha
        self.radius = radius
        self.epsilon = epsilon
        self.min_df_factor = minimum_df_factor

    def cluster_sentences(self, sentences: list):
        """clusters sentences using spherical kmeans"""
        spherical_kmeans = SphericalKMeans(
            n_clusters=self.num_clusters,
            max_iter=self.max_iter,
            sparsity=self.sparsity,
            init=self.init,
            tol=self.tol,
            verbose=self.verbose,
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
        """returns the hyper params of the clustering algorithm"""
        hyper_params = {
            "num_cluster": self.num_clusters,
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