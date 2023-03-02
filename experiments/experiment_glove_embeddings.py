import time
from enum import Enum
from pathlib import Path

import numpy
import numpy as np
from sklearn import metrics
from tqdm import tqdm

from dataset.customDataloader import get_dataloader
from gensim.models import KeyedVectors
from sklearn.cluster import KMeans, DBSCAN

not_properly_embedded = 0


class SentenceCitationFusingMethod(Enum):
    Concatenation = 1
    Averaging = 2


"""
gets the glove_embeddings as gensim KeyedVectors
----------
glove_embeddings_path : str
    path to the glove embeddings saved as txt
"""


def get_glove_embeddings_keyed_vectors(glove_embeddings_path):
    word2vec_glove_file = glove_embeddings_path.split('.txt')[0] + "word2vec" + ".kv"
    if Path(word2vec_glove_file).is_file():
        return KeyedVectors.load(word2vec_glove_file)
    else:
        keyed_vecs = KeyedVectors.load_word2vec_format(glove_embeddings_path, binary=False, no_header=True)
        keyed_vecs.save(word2vec_glove_file)
        return keyed_vecs


"""
converts a sentence into glove embeddings
if words are not part of the dictionary they are mapped to the zero vector
----------
sentence : str
    the string that is to be embedded
glove_embeddings: KeyedVectors
    a gensim object specifically made for storing word embeddings
embedding_dimension: int
    the used dimension for the word embeddings
"""


def convert_sentence_2_glove_embedding(sentence: str, glove_embeddings: KeyedVectors, embedding_dimension: int):
    numpy.seterr(all='raise')
    words = sentence.lower().split()
    count = 0
    sentence_embedding = np.zeros(embedding_dimension)
    word_embeddings = []
    for word in words:
        try:
            word_embeddings.append(glove_embeddings[word])
            count += 1
        except KeyError:
            continue
        except FloatingPointError:
            print("ERROR!")

    if count != 0:
        return np.mean(np.array(word_embeddings), axis=0, dtype=np.float64)
    else:
        print("Count==0 for:", sentence)
        return sentence_embedding


"""
sentence_citation_fusing_method: SentenceCitationPoolingMethod
    method to be used for fusing sentence and citation concat or average
"""


def fuse_sentence_and_citation_embedding(sentence_embedding, sentence_citation_embedding,
                                         sentence_citation_fusing_method: SentenceCitationFusingMethod):
    if sentence_citation_fusing_method == SentenceCitationFusingMethod.Averaging:
        return (sentence_embedding + sentence_citation_embedding) / 2
    if sentence_citation_fusing_method == SentenceCitationFusingMethod.Concatenation:
        return np.concatenate((sentence_embedding, sentence_citation_embedding), axis=None)


"""
calculates the correct labels and swaps them in place
this is necessary to make evaluation easier otherwise the clusterlabels would just be the database indexes
______
labels:list[int]
    list of labels, the ith position in the list corresponds to the ith example that is to be clustered 
"""
def calculate_correct_labels(labels:list[int]):
    label_cluster_index = 0
    label_map = {}
    for label_index, label in enumerate(labels):
        if label not in label_map:
            label_map[label] = label_cluster_index
            label_cluster_index += 1
        labels[label_index] = label_map[label]
    return None

"""
clusters with kmeans
"""
def cluster_with_kmeans(bag_of_sentences:list[str],number_of_clusters:int):
    km = KMeans(
        n_clusters=number_of_clusters, init='random',
        n_init=10, max_iter=300,
        tol=1e-04, random_state=0
    )
    labels_predicted = km.fit_predict(np.array(bag_of_sentences))
    return labels_predicted


def cluster_with_dbscan(bag_of_sentences:list[str]):
    db = DBSCAN(eps=1.5, min_samples=1, metric="euclidean").fit(bag_of_sentences)
    labels_predicted = db.labels_
    return labels_predicted
def main():

    # is one at the moment makes iterating easier, batch size of 200 would save some sekonds of execute
    batch_size = 1
    dataloader = get_dataloader(batch_size,shuffle=False)
    count = 0
    start = time.time()
    #gets the glove embeddings keyed vector in essence just a big lookup table to get embeddings for different words
    glove_embeddings_path = "embeddings/glove/glove.840B.300d.txt"
    #has to match dimension of embeddings used!
    glove_embeddings_dimension = 300
    glove_embeddings = get_glove_embeddings_keyed_vectors(glove_embeddings_path)

    #Adjusted Rand index as performance measure of the clustering
    ARI = 0

    not_properly_embedded_sentence = 0
    not_properly_embedded_citation = 0
    sentence_count = 0


    for i, data in enumerate(tqdm(dataloader)):
        sentences, labels = data[0]
        bag_of_sentences = []
        calculate_correct_labels(labels)
        sentence_count += len(sentences)
        for sentence_index, sentence in enumerate(sentences):
            sentence_embedding = convert_sentence_2_glove_embedding(sentence["sentence"], glove_embeddings,
                                                                    glove_embeddings_dimension)
            sentence_citation_embedding = convert_sentence_2_glove_embedding(sentence["citation_title"],
                                                                             glove_embeddings,
                                                                             glove_embeddings_dimension)
            overall_embedding = fuse_sentence_and_citation_embedding(sentence_embedding,
                                                                     sentence_citation_embedding,
                                                                     SentenceCitationFusingMethod.Averaging)
            bag_of_sentences.append(overall_embedding)

            #checks if its the zero vector if its zero vector its not embedded correctly
            if not np.any(sentence_citation_embedding):
                not_properly_embedded_citation += 1
            if not np.any(sentence_embedding):
                not_properly_embedded_sentence +=1

        # cluster the stuff:
        #labels_predicted = cluster_with_kmeans(bag_of_sentences, 1)
        labels_predicted = cluster_with_dbscan(bag_of_sentences)

        current_ari = metrics.adjusted_rand_score(labels, labels_predicted)
        ARI += current_ari/len(dataloader)
        count += 1

    end = time.time()
    print("count", count)
    print("time", -start + end)
    print("ARI:", ARI)
    print("sentence_count",sentence_count)
    print("notpropembeddedsentence",not_properly_embedded_sentence,"perc_",not_properly_embedded_sentence/sentence_count)
    print("notpropembeddedcitation",not_properly_embedded_citation,"perc_",not_properly_embedded_citation/sentence_count)

if __name__ == "__main__":
    main()
