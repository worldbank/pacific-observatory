import pandas as pd

def read_epu_files(data_dir, countries_slugs):
    epu_list = []
    for country in countries_slugs:
        epu_file = data_dir / f"{country}/epu/{country}_epu.csv"
        epu = pd.read_csv(epu_file)
        epu["date"] = pd.to_datetime(epu["date"], format="mixed")
        epu["epu_weighted_ma3"] = epu["epu_weighted"].rolling(window=3).mean()
        epu_news_count_cols = [col for col in epu.columns if "epu_count" in col]
        epu[f"epu_news_count"] = epu[epu_news_count_cols].sum(axis=1)
        epu['country'] = country
        epu = epu[["date", "country", "epu_unweighted", "epu_weighted", "epu_weighted_ma3", "epu_news_count", "news_total"]]
        epu_list.append(epu)
    return pd.concat(epu_list).reset_index(drop=True)

def read_epu_topics_files(data_dir, topics, countries_slugs):
    epu_list = []
    for country in countries_slugs:
        epu_topics_list = []
        for topic in topics:
            epu_topics_file = data_dir / f"{country}/epu/{country}_epu_{topic}.csv"
            epu_topics = pd.read_csv(epu_topics_file)
            epu_topics["date"] = pd.to_datetime(epu_topics["date"], format="mixed")
            epu_topics['country'] = country
            epu_news_count_cols = [col for col in epu_topics.columns if "epu_count" in col]
            epu_topics[f"{topic}_epu_news_count"] = epu_topics[epu_news_count_cols].sum(axis=1)
            epu_topics = epu_topics[["date", "country", f"epu_{topic}", f"{topic}_epu_news_count"]]
            epu_topics_list.append(epu_topics.set_index(['date','country']))

        topic_output = pd.concat(epu_topics_list, axis= 1)
        
        epu_list.append(topic_output)
    return pd.concat(epu_list).reset_index()

def read_sentiment_files(data_dir, countries_slugs):
    sentiment_list = []
    for country in countries_slugs:
        sentiment_file = data_dir / f"{country}/sentiment/{country}_sentiment.csv"
        sentiment = pd.read_csv(sentiment_file)
        sentiment["date"] = pd.to_datetime(sentiment["date"], format="mixed")
        sentiment['country'] = country
        sentiment = sentiment.rename(columns={"score": "sentiment_score", "z_score": "sentiment_z_score"})
        sentiment_list.append(sentiment)
    return pd.concat(sentiment_list).reset_index(drop=True)

def group_monthly(data):
    # This function should average scores like epu_weighted, epu_unweighted, and sentiment scores
    # and sum news counts per month
    data["date"] = pd.to_datetime(data["date"], format="mixed")
    data["date"] = data["date"].apply(lambda x: pd.to_datetime(str(x.year) + '-' + str(x.month).zfill(2) + '-01'))
    date_country_cols = ["date", "country"]
    sum_columns = [col for col in data.columns if "news_count" in col]
    mean_columns = [col for col in data.columns if ("epu_" in col) | ("sentiment_" in col)]
    sum_data = data[date_country_cols + sum_columns].groupby(date_country_cols).sum()
    mean_data = data[date_country_cols + mean_columns].groupby(date_country_cols).mean()
    data = pd.concat([sum_data, mean_data], axis=1)
    data = data.reset_index()
    
    return data

