from experiments.clustering_methods.clustering_interface import ClusteringInterface
from sklearn.mixture import GaussianMixture


class GMMClustering(ClusteringInterface):
    def __init__(self, n_components:int, covariance_type:str="full", tol:float=1e-3, reg_covar:float=1e-6, max_iter:int=100, n_init:int=1, init_params:str="k-means++", random_state=None,
                 warm_start:bool=False):
        self.n_components = n_components
        self.covariance_type = covariance_type
        self.tol = tol
        self.reg_covar = reg_covar
        self.max_iter = max_iter
        self.n_init = n_init
        self.init_params = init_params
        self.random_state = random_state
        self.warm_start = warm_start

    def cluster_sentences(self, sentences: list):
        """clusters sentences using gmm"""
        gmm = GaussianMixture(n_components=self.n_components).fit(sentences)
        labels = gmm.predict(sentences)
        return labels

    def return_hyper_params(self):
        """returns the hyper params of the clustering algorithm"""
        hyper_params = {"n_components": self.n_components, "covariance_type": self.covariance_type, "tol": self.tol,
                        "reg_covar": self.reg_covar, "max_iter": self.max_iter, "n_init": self.n_init,
                        "init_params": self.init_params, "random_state": self.random_state,
                        "warm_start": self.warm_start}
        return hyper_params
