from experiments.clustering_methods.clustering_interface import ClusteringInterface
from sklearn.mixture import GaussianMixture
from numpy import argmax, asarray


class GMMClustering(ClusteringInterface):
    def __init__(self, n_components: int = None, max_range: int = 20, covariance_type: str = "full", tol: float = 1e-3,
                 reg_covar: float = 1e-6,
                 max_iter: int = 100, n_init: int = 1, init_params: str = "k-means++", weights_init=None,
                 means_init=None, precisions_init=None, random_state=None,
                 warm_start: bool = False, verbose: int = 0, verbose_interval: int = 10):
        """Creates a GMMClustering object with the according parameters. The created GMM has the same parameters

                  Attributes
                  ----------
                  n_components : int, required
                      The number of mixture components.

                  max_range : int, default: 20
                    The range of components to evaluate the BIC criterion for determining
                    the optimal component number if no cluster number is given at initialization

                  covariance_type : {‘full’, ‘tied’, ‘diag’, ‘spherical’}, default=’full’
                      String describing the type of covariance parameters to use. Must be one of:
                         ‘full’: each component has its own general covariance matrix.
                         ‘tied’: all components share the same general covariance matrix.
                         ‘diag’: each component has its own diagonal covariance matrix.
                         ‘spherical’: each component has its own single variance.

                  tol : float, default=1e-3
                      The convergence threshold. EM iterations will stop when the lower bound average gain is below this threshold.

                  reg_covar : float, default=1e-6
                      Non-negative regularization added to the diagonal of covariance. Allows to assure that the covariance matrices are all positive.

                  max_iter : int, default=100
                      The number of EM iterations to perform.

                  n_init : int, default=1
                      The number of initializations to perform. The best results are kept.

                  init_params : {‘kmeans’, ‘k-means++’, ‘random’, ‘random_from_data’}, default=’k-means++’
                      The method used to initialize the weights, the means and the precisions. String must be one of:
                         ‘kmeans’ : responsibilities are initialized using kmeans.
                         ‘k-means++’ : use the k-means++ method to initialize.
                         ‘random’ : responsibilities are initialized randomly.
                         ‘random_from_data’ : initial means are randomly selected data points.

                  weights_init : array-like of shape (n_components, ), default=None
                      The user-provided initial weights. If it is None, weights are initialized using the init_params method.

                  means_init : array-like of shape (n_components, n_features), default=None
                      The user-provided initial means, If it is None, means are initialized using the init_params method.

                  precisions_init : array-like, default=None
                      The user-provided initial precisions (inverse of the covariance matrices). If it is None, precisions are initialized using the ‘init_params’ method. The shape depends on ‘covariance_type’:
                      (n_components,)                        if 'spherical',
                      (n_features, n_features)               if 'tied',
                      (n_components, n_features)             if 'diag',
                      (n_components, n_features, n_features) if 'full'

                  random_state : int, RandomState instance or None, default=None
                      Controls the random seed given to the method chosen to initialize the parameters (see init_params). In addition, it controls the generation of random samples from the fitted distribution (see the method sample). Pass an int for reproducible output across multiple function calls. See Glossary.

                  warm_start : bool, default=False
                      If ‘warm_start’ is True, the solution of the last fitting is used as initialization for the next call of fit(). This can speed up convergence when fit is called several times on similar problems. In that case, ‘n_init’ is ignored and only a single initialization occurs upon the first call. See the Glossary.

                  verbose : int, default=0
                      Enable verbose output. If 1 then it prints the current initialization and each iteration step. If greater than 1 then it prints also the log probability and the time needed for each step.

                  verbose_interval : int, default=10
                      Number of iteration done before the next print.
                  """
        self.n_components = n_components
        self.max_range = max_range
        self.covariance_type = covariance_type
        self.tol = tol
        self.reg_covar = reg_covar
        self.max_iter = max_iter
        self.n_init = n_init
        self.init_params = init_params
        self.weights_init = weights_init
        self.means_init = means_init
        self.precisions_init = precisions_init
        self.random_state = random_state
        self.warm_start = warm_start
        self.verbose = verbose
        self.verbose_interval = verbose_interval

    def cluster_sentences(self, sentences: list):
        """Creates a sklearn.mixtures.GaussianMixture object with the attributes of the GMMCLustering class,
        fit it to the data and returns the predicted cluster labels. If the number of smaples is less than the n_component
        attribute a GMM with n_component = number of samples is created.

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
        if self.n_components is None:
            self.n_components = self._find_k_with_bic(sentences)
        if num_samples == 1:
            return [0]
        elif num_samples < self.n_components:
            gmm = GaussianMixture(n_components=num_samples,
                                  covariance_type=self.covariance_type, tol=self.tol,
                                  reg_covar=self.reg_covar, max_iter=self.max_iter, n_init=self.n_init,
                                  weights_init=self.weights_init, means_init=self.means_init,
                                  precisions_init=self.precisions_init,
                                  init_params=self.init_params, random_state=self.random_state,
                                  warm_start=self.warm_start, verbose=self.verbose,
                                  verbose_interval=self.verbose_interval)
        else:
            gmm = GaussianMixture(n_components=self.n_components,
                                  covariance_type=self.covariance_type, tol=self.tol,
                                  reg_covar=self.reg_covar, max_iter=self.max_iter, n_init=self.n_init,
                                  weights_init=self.weights_init, means_init=self.means_init,
                                  precisions_init=self.precisions_init,
                                  init_params=self.init_params, random_state=self.random_state,
                                  warm_start=self.warm_start, verbose=self.verbose,
                                  verbose_interval=self.verbose_interval)
        gmm = gmm.fit(sentences)
        labels = gmm.predict(sentences)
        return labels

    def return_hyper_params(self):
        """Returns the attributes of the GMMClustering class, which are also the hyperparameter of the created GMM model in the cluster_sentence method.

        Returns
        -------
        hyper_params : dict
            a dictionary with the name of the hyperparameter and the corresponding value
        """

        hyper_params = {"n_components": self.n_components, "max_range": self.max_range,
                        "covariance_type": self.covariance_type, "tol": self.tol,
                        "reg_covar": self.reg_covar, "max_iter": self.max_iter, "n_init": self.n_init,
                        "init_params": self.init_params, "random_state": self.random_state,
                        "warm_start": self.warm_start}
        return hyper_params

    def _find_k_with_bic(self, sentences: list) -> int:
        """Private method to use bic criterion with the gmm model

                           Parameters
                           ----------
                           sentences : list
                               data to evaluate BIC criterion

                           Returns
                           -------
                           best_k : int
                               the best number of clusters.
                       """
        gm_bic = []
        gm_score = []
        for i in range(2, self.max_range):
            gm = GaussianMixture(n_components=self.n_components,
                                 covariance_type=self.covariance_type, tol=self.tol,
                                 reg_covar=self.reg_covar, max_iter=self.max_iter, n_init=self.n_init,
                                 weights_init=self.weights_init, means_init=self.means_init,
                                 precisions_init=self.precisions_init,
                                 init_params=self.init_params, random_state=self.random_state,
                                 warm_start=self.warm_start, verbose=0,
                                 verbose_interval=self.verbose_interval).fit(sentences)
            if self.verbose:
                print("BIC for number of cluster(s) {}: {}".format(i, gm.bic(asarray(sentences))))
                print("Log-likelihood score for number of cluster(s) {}: {}".format(i, gm.score(sentences)))
                print("-" * 100)
            gm_bic.append(-gm.bic(asarray(sentences)))
            gm_score.append(gm.score(sentences))

        best_score = argmax(gm_bic) + 2
        print(f"Selected optimal components: {best_score} ")
        return best_score
