import spacy
from sklearn.feature_extraction.text import TfidfVectorizer


class TfIdfEmbedding:
    def __init__(self):
        self.hyper_parameter = {
            'stop_words': {'english'},
            'lowercase': True, 
            'max_features': 20, 
            'strip_accents':{'ascii'}
        }
        self.vectorizer = TfidfVectorizer(self.hyper_parameter)
        self.nlp = spacy.load('en', disable=['parser', 'ner'])
        self.hyper_parameter['lemmatise'] = True
        
    def embed_sentences(self, document_sentences):
        if self.hyper_parameter['lemmatise']:
            document_sentences = self.lemmatise_sentences(document_sentences)
        return self.vectorizer.fit_transform(document_sentences)   
    
    def lemmatise_sentence(self, sentence):
        doc = self.nlp(sentence)
        return ' '.join([token.lemma_ for token in doc])
    
    def lemmatise_sentences(self, sentences):
        return [self.lemmatise_sentence(sentence) for sentence in sentences]
    
    def return_hyper_params(self):
        return self.hyper_parameter
    