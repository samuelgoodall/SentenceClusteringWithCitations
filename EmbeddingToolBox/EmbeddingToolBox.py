from sentence_transformers import SentenceTransformer
from typing import List
from torch import Tensor
from numpy import ndarray
from pandas import Series
from sklearn.feature_extraction.text import TfidfVectorizer


class EmbeddingToolBox:
    def __init__(self, senBERT_model: str = "all-MiniLM-L6-v2") -> None:
        self.senBERT_model = SentenceTransformer(senBERT_model)

    def set_senBERT_model(self, model_name: str) -> None:
        self.senBERT_model = model_name
        return None

    def encode_senBERT(
        self,
        sentences: str | List[str],
        batch_size: int = 32,
        show_progress_bar: bool = None,
        output_value: str = "sentence_embedding",
        convert_to_numpy: bool = True,
        convert_to_tensor: bool = False,
        convert_to_series: bool = False,
        device: str = None,
        normalize_embeddings: bool = False,
    ) -> List[Tensor] | ndarray | Tensor | Series:
        """
        Computes sentence embeddings
        :param sentences: the sentences to embed
        :param batch_size: the batch size used for the computation
        :param show_progress_bar: Output a progress bar when encode sentences
        :param output_value:  Default sentence_embedding, to get sentence embeddings. Can be set to token_embeddings to get wordpiece token embeddings. Set to None, to get all output values
        :param convert_to_numpy: If true, the output is a list of numpy vectors. Else, it is a list of pytorch tensors.
        :param convert_to_tensor: If true, you get one large tensor as return. Overwrites any setting from convert_to_numpy
        :param device: Which torch.device to use for the computation
        :param normalize_embeddings: If set to true, returned vectors will have length 1. In that case, the faster dot-product (util.dot_score) instead of cosine similarity can be used.
        :return:
           By default, a list of tensors is returned. If convert_to_tensor, a stacked tensor is returned. If convert_to_numpy, a numpy matrix is returned.
        """
        embeddings = self.senBERT_model.encode(
            sentences,
            batch_size,
            show_progress_bar,
            output_value,
            convert_to_numpy,
            convert_to_tensor,
            device,
            normalize_embeddings,
        )
        if convert_to_series:
            return Series(embeddings.tolist())
        return embeddings

    def encode_tfidf(self, sentences: str | List[str]) -> ndarray:
        """Convert a collection of raw documents to a matrix of TF-IDF features.
        Parameters
        ----------
        input : {'filename', 'file', 'content'}, default='content'
            - If `'filename'`, the sequence passed as an argument to fit is
            expected to be a list of filenames that need reading to fetch
            the raw content to analyze.
            - If `'file'`, the sequence items must have a 'read' method (file-like
            object) that is called to fetch the bytes in memory.
            - If `'content'`, the input is expected to be a sequence of items that
            can be of type string or byte.
        encoding : str, default='utf-8'
            If bytes or files are given to analyze, this encoding is used to
            decode.
        decode_error : {'strict', 'ignore', 'replace'}, default='strict'
            Instruction on what to do if a byte sequence is given to analyze that
            contains characters not of the given `encoding`. By default, it is
            'strict', meaning that a UnicodeDecodeError will be raised. Other
            values are 'ignore' and 'replace'.
        strip_accents : {'ascii', 'unicode'} or callable, default=None
            Remove accents and perform other character normalization
            during the preprocessing step.
            'ascii' is a fast method that only works on characters that have
            a direct ASCII mapping.
            'unicode' is a slightly slower method that works on any characters.
            None (default) does nothing.
            Both 'ascii' and 'unicode' use NFKD normalization from
            :func:`unicodedata.normalize`.
        lowercase : bool, default=True
            Convert all characters to lowercase before tokenizing.
        preprocessor : callable, default=None
            Override the preprocessing (string transformation) stage while
            preserving the tokenizing and n-grams generation steps.
            Only applies if ``analyzer`` is not callable.
        tokenizer : callable, default=None
            Override the string tokenization step while preserving the
            preprocessing and n-grams generation steps.
            Only applies if ``analyzer == 'word'``.
        analyzer : {'word', 'char', 'char_wb'} or callable, default='word'
            Whether the feature should be made of word or character n-grams.
            Option 'char_wb' creates character n-grams only from text inside
            word boundaries; n-grams at the edges of words are padded with space.
            If a callable is passed it is used to extract the sequence of features
            out of the raw, unprocessed input.
            .. versionchanged:: 0.21
                Since v0.21, if ``input`` is ``'filename'`` or ``'file'``, the data
                is first read from the file and then passed to the given callable
                analyzer.
        stop_words : {'english'}, list, default=None
            If a string, it is passed to _check_stop_list and the appropriate stop
            list is returned. 'english' is currently the only supported string
            value.
            There are several known issues with 'english' and you should
            consider an alternative (see :ref:`stop_words`).
            If a list, that list is assumed to contain stop words, all of which
            will be removed from the resulting tokens.
            Only applies if ``analyzer == 'word'``.
            If None, no stop words will be used. max_df can be set to a value
            in the range [0.7, 1.0) to automatically detect and filter stop
            words based on intra corpus document frequency of terms.
        token_pattern : str, default=r"(?u)\\b\\w\\w+\\b"
            Regular expression denoting what constitutes a "token", only used
            if ``analyzer == 'word'``. The default regexp selects tokens of 2
            or more alphanumeric characters (punctuation is completely ignored
            and always treated as a token separator).
            If there is a capturing group in token_pattern then the
            captured group content, not the entire match, becomes the token.
            At most one capturing group is permitted.
        ngram_range : tuple (min_n, max_n), default=(1, 1)
            The lower and upper boundary of the range of n-values for different
            n-grams to be extracted. All values of n such that min_n <= n <= max_n
            will be used. For example an ``ngram_range`` of ``(1, 1)`` means only
            unigrams, ``(1, 2)`` means unigrams and bigrams, and ``(2, 2)`` means
            only bigrams.
            Only applies if ``analyzer`` is not callable.
        max_df : float or int, default=1.0
            When building the vocabulary ignore terms that have a document
            frequency strictly higher than the given threshold (corpus-specific
            stop words).
            If float in range [0.0, 1.0], the parameter represents a proportion of
            documents, integer absolute counts.
            This parameter is ignored if vocabulary is not None.
        min_df : float or int, default=1
            When building the vocabulary ignore terms that have a document
            frequency strictly lower than the given threshold. This value is also
            called cut-off in the literature.
            If float in range of [0.0, 1.0], the parameter represents a proportion
            of documents, integer absolute counts.
            This parameter is ignored if vocabulary is not None.
        max_features : int, default=None
            If not None, build a vocabulary that only consider the top
            max_features ordered by term frequency across the corpus.
            This parameter is ignored if vocabulary is not None.
        vocabulary : Mapping or iterable, default=None
            Either a Mapping (e.g., a dict) where keys are terms and values are
            indices in the feature matrix, or an iterable over terms. If not
            given, a vocabulary is determined from the input documents.
        binary : bool, default=False
            If True, all non-zero term counts are set to 1. This does not mean
            outputs will have only 0/1 values, only that the tf term in tf-idf
            is binary. (Set idf and normalization to False to get 0/1 outputs).
        dtype : dtype, default=float64
            Type of the matrix returned by fit_transform() or transform().
        norm : {'l1', 'l2'} or None, default='l2'
            Each output row will have unit norm, either:
            - 'l2': Sum of squares of vector elements is 1. The cosine
            similarity between two vectors is their dot product when l2 norm has
            been applied.
            - 'l1': Sum of absolute values of vector elements is 1.
            See :func:`preprocessing.normalize`.
            - None: No normalization.
        use_idf : bool, default=True
            Enable inverse-document-frequency reweighting. If False, idf(t) = 1.
        smooth_idf : bool, default=True
            Smooth idf weights by adding one to document frequencies, as if an
            extra document was seen containing every term in the collection
            exactly once. Prevents zero divisions.
        sublinear_tf : bool, default=False
            Apply sublinear tf scaling, i.e. replace tf with 1 + log(tf).
        Attributes
        ----------
        vocabulary_ : dict
            A mapping of terms to feature indices.
        fixed_vocabulary_ : bool
            True if a fixed vocabulary of term to indices mapping
            is provided by the user.
        idf_ : array of shape (n_features,)
            The inverse document frequency (IDF) vector; only defined
            if ``use_idf`` is True.
        stop_words_ : set
            Terms that were ignored because they either:
            - occurred in too many documents (`max_df`)
            - occurred in too few documents (`min_df`)
            - were cut off by feature selection (`max_features`)."""

        vectorizer = TfidfVectorizer()
        return vectorizer.fit_transform(sentences)
