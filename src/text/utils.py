import re
import pandas as pd
import spacy
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


def sent_to_words(sentences):
    for sentence in sentences:
        sentence = re.sub(r'\s', ' ', sentence).strip()
        yield (simple_preprocess(str(sentence), deacc=True))


def lemmatize_sent(sent, nlp, allowed_postags=['NOUN', 'ADJ', 'VERB', 'ADV']):
    doc = nlp(" ".join(sent))
    return [token.lemma_ for token in doc if token.pos_ in allowed_postags]


def make_phrases(texts, phrases_model):
    return [phrases_model[doc] for doc in texts]


def preprocess_text(texts,
                    stopwords,
                    bigram_mod,
                    trigram_mod,
                    nlp):

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
    dates_range = pd.date_range(start=min_date, end=max_date, freq=freq)
    dates_df = pd.DataFrame(dates_range, columns=["date"])
    if "date" in checked_df.columns:
        checked_df["date"] = pd.to_datetime(checked_df["date"], format="mixed")
        checked_df = dates_df.merge(checked_df, how="left", on="date").fillna(0)
        return checked_df
    else:
        raise ValueError("cannot find `date` column in dataframe being checked.")
