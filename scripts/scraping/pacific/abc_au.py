import os
import sys
from ..config import PROJECT_FOLDER_PATH, ABC_AU_TOPIC_DICT, SCRAPE_ALL
sys.path.insert(0, PROJECT_FOLDER_PATH)
import pandas as pd
import numpy as np
import json
from src.scraper.scrape import RequestsScraper
from src.scraper.utils import check_latest_date


def scrape_ajax_abc(document_id: int,
                    size: int = 1000,
                    offset: int = 0
                    ) -> list:

    scraper = RequestsScraper()
    output = []

    total = 5000
    while offset < total:
        ajax_url = f"https://www.abc.net.au/news-web/api/loader/topicstories?name=PaginationArticles&documentId={document_id}&offset={offset}&size={size}"
        content = scraper.request_url(ajax_url, timeout=30)
        data = json.loads(content)
        total = data["pagination"]["total"]
        for i in data["collection"]:
            link = i["link"]["to"]
            try:
                title = i["title"]["children"]
                date = i["timestamp"]["dates"]["firstPublished"]
                media_type = i["contentUri"].split("//")[-1].split("/")[0]
                output.append([link, title, date, media_type])
            except:
                output.append([link, np.NAN, np.NAN, np.NAN]) 
        offset += size
    return output


for key, name in ABC_AU_TOPIC_DICT.items():
    ## Scrape URLs
    output = scrape_ajax_abc(
        document_id = key
    )
    df = (pd.DataFrame(output, columns=["url", "title", "date", "media_type"])
            .drop_duplicates())
    df["url"] = ["https://www.abc.net.au" + i for i in df.url]
    df["date"] = pd.to_datetime(df["date"])
    target_dir = sys.path[0] + f"data/text/{name}/"
    df.to_csv(target_dir + name + "_abc_urls.csv", encoding="utf-8")

    ## Check gaps between scrapings
    news_filepath = target_dir + name + "_abc_news.csv"
    if os.path.exists(news_filepath): 
        previous_news_df = pd.read_csv(news_filepath).drop("Unnamed: 0", axis=1)
        previous_news_df["date"] = pd.to_datetime(previous_news_df["date"])
        latest_date = check_latest_date(target_dir + name + "_abc_news.csv")
        urls = df[(df.date > latest_date) & (df.media_type == "article")]["url"].tolist()
    else:
        SCRAPE_ALL=True
        urls = df[df.media_type == "article"]["url"].tolist()

    ## Scrape articles
    scraper = RequestsScraper(parser="html.parser")
    expressions = ['RelatedTopics_topicsList__R3TEv', 'paragraph_paragraph___QITb']
    print(f"{name}'s scraping work has started.")
    news_output = scraper.scrape_urls(urls, expressions, speed_up=True)
    news_list = []
    for i in news_output:
        url = i[0]
        if len(i[1]) != 0:
            if len(i[1][0]) > 0:
                tags = ''.join(j.text + ", " for j in i[1][0][0])
            else:
                tags = "Missing"
            news = ''.join(j.text for j in i[1][1])
        news_list.append([url, news, tags])

    news_df = pd.DataFrame(news_list, columns=["url", "news", "tags"])
    news_df = news_df.merge(df[["url", "date"]], how="left", on="url")
    if not SCRAPE_ALL:
        news_df = (pd.concat([previous_news_df, news_df], axis=0)
                     .sort_values(by="date", ascending=False)
                     .reset_index(drop=True))
        news_df.to_csv(target_dir + name + "_abc_news.csv", encoding="utf-8")