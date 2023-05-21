import itertools
import json
from os import path
import torch
from torch.utils.data import DataLoader
from tqdm import tqdm

from dataset.ArxivDataset import ArxivDataset
from dataset.ArxivDatasetPrecomputedEmbeddings import ArxivDatasetPrecomputedEmbeddings
from dataset.customDataloader import CustomDataLoader

from experiments.clustering_methods.db_scan_clustering import DBScanClustering
from experiments.clustering_methods.gmm_clustering import GMMClustering
from experiments.clustering_methods.spherical_kmeans_clustering import \
    SphericalKMeansClustering
from experiments.embedding_methods.bert_embedding import \
    BertTransformerEmbedding
from experiments.embedding_methods.embedding_interface import \
    EmbeddingInterface
from experiments.embedding_methods.fasttext_embedding import FastTextEmbedding
from experiments.embedding_methods.glove_embedding import GloveEmbedding
from experiments.embedding_methods.sentence_transformer_embedding import \
    SentenceTransformerEmbedding
from experiments.embedding_methods.tf_idf_embedding import TfIdfEmbedding
from experiments.evaluation import (evaluate,
                                    evaluate_with_precomputed_embeddings)


def conduct_experiment(embedding: EmbeddingInterface, dataloader: DataLoader = None):
    """
    conducts a single experiment for an embedding

    Parameters
    ----------
    embedding : EmbeddingInterface
        The embedding to be used
    dataloader: DataLoader
        the dataloader for the dataset to be iterated
    """
    gmm_clustering = GMMClustering()
    db_scan_clustering = DBScanClustering()
    spherical_kmeans_clustering = SphericalKMeansClustering()
    clustering_methods = [db_scan_clustering,gmm_clustering,spherical_kmeans_clustering]
    for clustering in clustering_methods:
        evaluate(embedding=embedding, clustering=clustering, dataloader=dataloader, use_citation=True)
        evaluate(embedding=embedding, clustering=clustering, dataloader=dataloader, use_citation=False)



def conduct_experiment_precomputed_embedding(embedding: EmbeddingInterface, dataloader: DataLoader = None):
    """
    conducts a single experiment for a dataset with the embeddings already computed

    Parameters
    ----------
    embedding : EmbeddingInterface
        The embedding to be used
    dataloader: DataLoader
        the dataloader for the dataset to be iterated
    """
    gmm_clustering = GMMClustering()
    db_scan_clustering = DBScanClustering()
    spherical_kmeans_clustering = SphericalKMeansClustering()
    clustering_methods = [gmm_clustering, spherical_kmeans_clustering, db_scan_clustering]
    for clustering in clustering_methods:
        evaluate_with_precomputed_embeddings(embedding=embedding, clustering=clustering,
                                             dataloader=dataloader, use_citation=True)
        evaluate_with_precomputed_embeddings(embedding=embedding, clustering=clustering,
                                             dataloader=dataloader, use_citation=False)


def main():
    """
    Script used for conducting the experiments
    """
    generator = torch.Generator().manual_seed(42)

    glove_embeddings_path = "/embedding_methods/embeddings/glove/glove.42B.300d.txt"
    glove_embedding = GloveEmbedding(300, glove_embeddings_path)
    fastText_embedding = FastTextEmbedding(300, "/embedding_methods/embeddings/FastText/cc.en.300.bin")
    bert_embedding = BertTransformerEmbedding("bert-base-uncased")
    sentence_transformer_embedding = SentenceTransformerEmbedding("all-mpnet-base-v2")
    tfidf_embedding = TfIdfEmbedding()

    # is one at the moment makes iterating easier, batch size of 200 would save some seconds of execute
    batch_size = 1
    unlemmatized_dataset = ArxivDataset(path.abspath("../dataset/database/dataset_new.db"))

    # the train, test and validation indexes have to be the same for all experiments in order to have comparability
    train_indexes, test_indexes, validation_indexes = CustomDataLoader.get_train_test_validation_index_split(
        train_test_validation_split=[0.8, 0.2, 0.0],
        fixed_random_generator=generator, dataset=unlemmatized_dataset)

    indexes = {"train":train_indexes,"test":test_indexes,"validation":validation_indexes}
    with open('../train_test_validation.json', 'w') as fp:
        json.dump(indexes, fp)
    unlemmatized_dataloader_train, unlemmatized_dataloader, unlemmatized_dataloader_validation = CustomDataLoader.get_train_test_validation_split_indexbased_dataloader(
        train_idx=train_indexes, test_idx=test_indexes, val_idx=validation_indexes, batch_size=batch_size,
        shuffle=False, dataset=unlemmatized_dataset)
    lemmatized_dataset = ArxivDataset(path.abspath("../dataset/database/dataset_new_lemmatized.db"))
    lemmatized_dataloader_train, lemmatized_dataloader, lemmatized_dataloader_validation = CustomDataLoader.get_train_test_validation_split_indexbased_dataloader(
        train_idx=train_indexes, test_idx=test_indexes, val_idx=validation_indexes, batch_size=batch_size,
        shuffle=False,
        dataset=lemmatized_dataset)
    setup_tfidf_embeddings(tfidf_embedding, lemmatized_dataloader_train)
    sentence_transformer_dataset = ArxivDatasetPrecomputedEmbeddings("../dataset/database/dataset_new_precomputed_embeddings_sentence_transformer.db")
    sentence_transformer_dataloader_train, sentence_transformer_dataloader, sentence_transformer_dataloader_validation = CustomDataLoader.get_train_test_validation_split_indexbased_dataloader(
        train_idx=train_indexes, test_idx=test_indexes, val_idx=validation_indexes, batch_size=batch_size,
        shuffle=False,
        dataset=sentence_transformer_dataset)
    bert_dataset = ArxivDatasetPrecomputedEmbeddings("../dataset/database/dataset_new_precomputed_embeddings_bert.db")
    bert_dataloader_train, bert_dataloader, bert_dataloader_validation = CustomDataLoader.get_train_test_validation_split_indexbased_dataloader(
        train_idx=train_indexes, test_idx=test_indexes, val_idx=validation_indexes, batch_size=batch_size,
        shuffle=False,
        dataset=bert_dataset)
    conduct_experiment_precomputed_embedding(embedding=bert_embedding, dataloader=bert_dataloader)
    conduct_experiment_precomputed_embedding(embedding=sentence_transformer_embedding, dataloader=sentence_transformer_dataloader)
    conduct_experiment(embedding=glove_embedding, dataloader=lemmatized_dataloader)
    conduct_experiment(embedding=fastText_embedding, dataloader=unlemmatized_dataloader)
    conduct_experiment(embedding=tfidf_embedding, dataloader=lemmatized_dataloader)

    
def setup_tfidf_embeddings(tfidf_embedding: TfIdfEmbedding, dataloader: DataLoader):
    try:
        tfidf_embedding.load()
    except:
        print("Setup TfIdf Embedding")
        all_sentences = []
        for i, data in enumerate(tqdm(dataloader)):
            sentences, labels = data[0]
            all_sentences.append(sentences)
        all_sentences = list(itertools.chain.from_iterable(all_sentences))
        tfidf_embedding.setup(all_sentences=all_sentences)
        print("TFIdf Embeddings setup!")

if __name__ == "__main__":
    main()
