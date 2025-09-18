import gensim
from gensim.models import CoherenceModel

def compute_coherence_values(dictionary,
                             corpus,
                             texts,
                             mallet_path,
                             limit,
                             start=2,
                             step=1):
    """
    Compute coherence values for a range of LDA topic models.

    Parameters:
        dictionary (gensim.corpora.Dictionary): The dictionary mapping words to IDs.
        corpus (list of list of int): The document-term matrix.
        texts (list of list of str): Preprocessed texts.
        mallet_path (str, optional): Path to the Mallet LDA binary.
        limit (int): The maximum number of topics to explore.
        start (int, optional): The starting number of topics. Default is 2.
        step (int, optional): The step size for the number of topics. Default is 1.
    Returns:
        tuple: A tuple containing a list of models and a list of coherence values.
    """
    coherence_values = []
    model_list = []
    for num_topics in range(start, limit, step):
        model = gensim.models.wrappers.LdaMallet(mallet_path,
                                                 corpus=corpus,
                                                 num_topics=num_topics,
                                                 id2word=dictionary)
        model_list.append(model)
        coherencemodel = CoherenceModel(model=model,
                                        texts=texts,
                                        dictionary=dictionary,
                                        coherence='c_v')
        coherence_values.append(coherencemodel.get_coherence())
        
    return model_list, coherence_values