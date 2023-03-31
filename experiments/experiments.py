from torch.utils.data import DataLoader

from dataset.customDataloader import get_train_test_validation_dataloader, get_dataloader
from experiments.clustering_methods.db_scan_clustering import DBScanClustering
from experiments.clustering_methods.spherical_kmeans_clustering import SphericalKMeansClustering
from experiments.embedding_methods.bert_embedding import BertTransformerEmbedding
from experiments.embedding_methods.embedding_interface import EmbeddingInterface
from experiments.embedding_methods.fasttext_embedding import FastTextEmbedding
from experiments.embedding_methods.glove_embedding import GloveEmbedding
from experiments.embedding_methods.sbert_embedding import SentenceTransformerEmbedding
from experiments.evaluation import evaluate


def conduct_experiment(embedding:EmbeddingInterface,dataloader: DataLoader = None):
    """
    conducts a single experiment for an embedding

    Parameters
    ----------
    embedding : EmbeddingInterface
        The embedding to be used
    dataloader: str
        the dataloader for the dataset to be iterated
    """
    gmm_clustering = None
    db_scan_clustering = DBScanClustering()
    spherical_kmeans_clustering = SphericalKMeansClustering()
    clustering_methods = [gmm_clustering,db_scan_clustering,spherical_kmeans_clustering]
    for clustering in clustering_methods:
        evaluate(embedding=embedding, clustering=clustering, dataloader=dataloader, use_citation=True)
        evaluate(embedding=embedding, clustering=clustering, dataloader=dataloader, use_citation=False)





def main():
    """
    Script used for conducting the experiments
    """

    glove_embeddings_path = "../experiments/embedding_methods/embeddings/glove/glove.42B.300d.txt"
    glove_embedding = GloveEmbedding(300, glove_embeddings_path)
    fastText_embedding = FastTextEmbedding(300, "../experiments/embedding_methods/embeddings/FastText/cc.en.300.bin")
    bert_embedding = BertTransformerEmbedding("")
    sbert_embedding = SentenceTransformerEmbedding("")

    # is one at the moment makes iterating easier, batch size of 200 would save some seconds of execute
    batch_size = 1
    unlemmatized_dataloader = get_dataloader(batch_size,shuffle=False,dataset_location="../dataset/database/dataset_new.db")
    lemmatized_dataloader = get_dataloader(batch_size, shuffle=False,dataset_location="../dataset/database/dataset_new_lemmatized.db")

    conduct_experiment(embedding=glove_embedding,dataloader=lemmatized_dataloader)
    conduct_experiment(embedding=fastText_embedding,dataloader=unlemmatized_dataloader)
    conduct_experiment(embedding=bert_embedding,dataloader=unlemmatized_dataloader)
    conduct_experiment(embedding=sbert_embedding,dataloader=unlemmatized_dataloader)






if __name__ == "__main__":
    main()