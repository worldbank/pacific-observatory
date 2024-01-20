import os
import sys
from ..config import PROJECT_FOLDER_PATH, SOLOMON_STAR_URLS, SCRAPE_ALL
sys.path.insert(0, PROJECT_FOLDER_PATH)
import numpy as np
import pandas as pd
from src.scraper.scrape import WebScraper

SCRAPE_ALL = True

target_dir = sys.path[0] + "data/text/solomon_islands/"
scraper = WebScraper('html.parser')

pages_raw = scraper.scrape_urls(SOLOMON_STAR_URLS,
                                ["blog-content wf-td", "entry-title", "entry-date"],
                                speed_up=True)

urls_info = []
for page in pages_raw:
    for (url_entry, title_entry, date_entry) in zip(*page[1]):
        url = (url_entry.find("a")["href"])
        title = title_entry.text
        date = date_entry.text
        urls_info.append([url, date, title])

urls_df = pd.DataFrame(urls_info, columns=["url", "date", "title"])
urls_df["date"] = pd.to_datetime(urls_df["date"], format="mixed")
urls_df = (urls_df.sort_values(by="date", ascending=False)
           .reset_index(drop=True))
urls_df.to_csv(target_dir + "solomon_star_urls.csv", encoding="utf-8")


previous_news_df = pd.read_csv(
    target_dir + "solomon_star_news.csv").drop("Unnamed: 0", axis=1)
previous_news_df["date"] = pd.to_datetime(
    previous_news_df["date"], format="mixed")
if not SCRAPE_ALL:
    previous_urls = set(previous_news_df["url"])
    current_urls = set(urls_df["url"])
    urls_to_scrape = list(current_urls - previous_urls)
else:
    urls_to_scrape = urls_df["url"].tolist()

news_raw = scraper.scrape_urls(urls_to_scrape,
                               ["entry-content", "category-link"],
                               speed_up=True)
news_info = []
for i in news_raw:
    url = i[0]
    for (text_entry, tag_entry) in zip(*i[1]):
        text = " ".join(p.text for p in text_entry.find_all("p"))
        tag = ", ".join(p.text for p in tag_entry.find_all("a"))
        news_info.append([url, text, tag])

news_df = pd.DataFrame(news_info, columns=["url", "news", "tag"])
news_df = news_df.merge(urls_df[["url", "date"]], how="left", on="url")

if not SCRAPE_ALL:
    current_news_df = pd.concat([news_df, previous_news_df], axis=0)
    current_news_df = (current_news_df.sort_index(by="date", ascending=False)
                        .reset_index(drop=true))
    current_news_df.to_csv(target_dir + "solomon_star_news.csv", encoding="utf-8")
else:
    news_df.to_csv(target_dir + "solomon_star_news.csv", encoding="utf-8")