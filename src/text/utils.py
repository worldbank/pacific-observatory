"""
The module provides a series of text preprocessing supporting utils.

Last modified:
    2024-02-05
"""
import re
import spacy
from typing import List, Any
import pandas as pd
from gensim.utils import simple_preprocess


def is_in_word_list(row: str, terms: list) -> bool:
    """
    Check if any of the given terms are present in the input row.

    Args:
        row (str): The input row to search for terms in.
        terms (list): A list of terms to search for in the row.

    Returns:
        bool: True if any of the terms are found in the row, False otherwise.
    """
    return any([word in str(row) for word in terms])


def sent_to_words(sentences: List[str]):
    """
    Converts sentences into a list of words, performing simple preprocessing.

    Args:
        sentences: A list of sentences to be converted.

    Yields:
        A generator yielding lists of words extracted from each sentence after preprocessing.
    """
    for sentence in sentences:
        sentence = re.sub(r'\s', ' ', sentence).strip()
        yield (simple_preprocess(str(sentence), deacc=True))


def lemmatize_sent(sent,
                   nlp,
                   allowed_postags=['NOUN', 'ADJ', 'VERB', 'ADV']):
    """
    Lemmatizes words in a sentence based on allowed part-of-speech tags.

    Args:
        sent: The sentence represented as a list of words.
        nlp: An instance of spacy's language model.
        allowed_postags: List of part-of-speech tags allowed for lemmatization.

    Returns:
        A list of lemmatized words filtered by allowed part-of-speech tags.
    """
    doc = nlp(" ".join(sent))
    return [token.lemma_ for token in doc if token.pos_ in allowed_postags]


def make_phrases(texts: List[str],
                 phrases_model):
    """
    Apply phrase models to texts to detect and join multi-word expressions.

    Args:
        texts: List of tokenized texts.
        phrases_model: A Phraser model that detects phrases.

    Returns:
        A list of texts with phrases detected and joined.
    """
    return [phrases_model[doc] for doc in texts]


def preprocess_text(texts: List[str],
                    stopwords: List[str],
                    bigram_mod,
                    trigram_mod,
                    nlp: spacy.language.Language):
    """
    Preprocesses texts by removing stopwords, applying bigram and trigram models, and lemmatizing.

    Args:
        texts: List of texts to preprocess.
        stopwords: List of stopwords to remove.
        bigram_mod: Bigram Phraser model.
        trigram_mod: Trigram Phraser model.
        nlp: An instance of spacy's language model for lemmatization.

    Returns:
        A list of preprocessed and lemmatized texts.
    """
    texts_no_stopwords = [[
        word for word in simple_preprocess(str(doc))
        if word not in stopwords
    ] for doc in texts]
    print("Stopwords has been done.")
    texts_bigrams = make_phrases(texts_no_stopwords, bigram_mod)
    texts_trigrams = make_phrases(texts_bigrams, trigram_mod)
    texts_lemmatized = [lemmatize_sent(doc, nlp) for doc in texts_trigrams]

    return texts_lemmatized


def generate_continous_df(checked_df: pd.DataFrame,
                          min_date: str, max_date: str, freq="MS"):
    """
    Generates a continuous date range dataframe and merges it with an existing dataframe.

    Args:
        checked_df: The dataframe to merge with the continuous date range.
        min_date: The start date for the continuous date range.
        max_date: The end date for the continuous date range.
        freq: The frequency of the dates to generate, defaults to 'MS' (month start).

    Returns:
        A dataframe with a continuous date range merged with the existing dataframe.

    Raises:
        ValueError: If 'date' column is not found in the checked dataframe.
    """
    dates_range = pd.date_range(start=min_date, end=max_date, freq=freq)
    dates_df = pd.DataFrame(dates_range, columns=["date"])
    if "date" in checked_df.columns:
        checked_df["date"] = pd.to_datetime(checked_df["date"], format="mixed")
        checked_df = dates_df.merge(
            checked_df, how="left", on="date").fillna(0)
        return checked_df
    else:
        raise ValueError(
            "cannot find `date` column in dataframe being checked.")
