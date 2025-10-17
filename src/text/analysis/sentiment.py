from nltk.sentiment.vader import SentimentIntensityAnalyzer
from dateutil.parser import parse
import pandas as pd

def sentiment_analysis(df):

    sid = SentimentIntensityAnalyzer()
    results = []
    for news in df.news:
        scores = sid.polarity_scores(str(news))
        results.append(scores)
    return results


def calculate_sentiment(df):

    df = df[(df.econ) & (df.policy)].reset_index(drop=True)

    sent_res = sentiment_analysis(df)

    df["score"] = [i["compound"] for i in sent_res]
    df["date"] = df["date"].apply(lambda x: parse(str(x)).date())
    df["date"] = pd.to_datetime(df["date"])
    month_sent = (df.set_index("date").groupby(
        pd.Grouper(freq="MS"))[["score"]].mean().reset_index())

    return month_sent, df.score.mean(), df.score.std()