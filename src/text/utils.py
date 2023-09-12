import re
import gensim
import gensim.corpora as corpora
from gensim.utils import simple_preprocess
from gensim.models import CoherenceModel 

def sent_to_words(sentences):
    for sentence in sentences:
        sentence = re.sub(r'\s', ' ', sentence).strip()
        yield (gensim.utils.simple_preprocess(str(sentence), deacc=True))

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
        word for word in gensim.utils.simple_preprocess(str(doc))
        if word not in stopwords
    ] for doc in texts]
    print("Stopwords has been done.")
    texts_bigrams = make_phrases(texts_no_stopwords, bigram_mod)
    texts_trigrams = make_phrases(texts_bigrams, trigram_mod)
    texts_lemmatized = [lemmatize_sent(doc, nlp) for doc in texts_trigrams]

    return texts_lemmatized