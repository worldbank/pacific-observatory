import os
import sys
import pandas as pd
import re
import numpy as np
from config import (PROJECT_FOLDER_PATH, MATANGI_PAGE_URLS,
                    MATANGI_PAGE_URLS_ELEMENTS, SCRAPE_ALL)
sys.path.insert(0, PROJECT_FOLDER_PATH)
from src.scraper.scrape import WebScraper
from src.scraper.utils import check_latest_date, handle_mixed_dates

target_dir = sys.path[0] + "data/text/tonga/"
if not os.path.exists(target_dir):
    os.mkdir(target_dir)


mtg = WebScraper("html.parser")
urls_raw = mtg.scrape_urls(MATANGI_PAGE_URLS, MATANGI_PAGE_URLS_ELEMENTS,
                           speed_up=True)
urls_info = {
    "url": [],
    "date": [],
    "title": [],
    "tag": [],
    "location": [],
}
for page in urls_raw:
    page_url, page_raw = page[0], page[1]
    urls_info["title"].extend([i.text for i in page_raw[0]])
    urls_info["url"].extend([i.find("a")["href"] for i in page_raw[0]])
    urls_info["date"].extend([i.text for i in page_raw[2]])
    urls_info["tag"].extend([i.text for i in page_raw[1]])
    urls_info["location"].extend([i.text.strip() for i in page_raw[3]])

mtg_urls = pd.DataFrame(urls_info)
mtg_urls["url"] = [f"https://matangitonga.to{url}" for url in mtg_urls.url]

def date_extractor(date, pattern=r"\b\d{1,2}\s\w+\s\d{4}\b"):
    if len(date.strip()) != 0:
        try: 
            formatted_date = re.findall(pattern, date)[0]
            return formatted_date
        except:
            return date
    else:
        return np.NAN

mtg_urls["date"] = pd.to_datetime(mtg_urls["date"].apply(lambda x: date_extractor(x)),
                                  format="mixed")

print_urls = mtg_urls["url"].tolist()
print_urls_raw = mtg.scrape_urls(print_urls, ["print-page"], speed_up=True)

# Create a mapping between page urls and print-page urls
urls_mapping = []
for i in print_urls_raw:
    original_url = i[0]
    if len(i[1][0]) != 0:
        print_url = i[1][0][0]["href"]
    else:
        print_url = np.NAN
    urls_mapping.append([original_url, print_url])
urls_map_df = pd.DataFrame(urls_mapping, columns=["url", "print_url"])
mtg_urls = mtg_urls.merge(urls_map_df, how="left", on="url") 
mtg_urls.to_csv(f"{target_dir}matangi_urls.csv", encoding="utf-8")

#
previous_news_df = pd.read_csv(target_dir + "matangi_news.csv").drop("Unnamed: 0", axis=1)
latest_date = check_latest_date(target_dir + "matangi_news.csv")
mtg_urls["tonga"] = mtg_urls["location"].apply(lambda x: "tonga" in str(x).lower())

if not SCRAPE_ALL: 
    news_urls = mtg_urls[(mtg_urls["tonga"] == True) & (mtg_urls["date"] >= latest_date)]["print_url"].tolist()
else:
    news_urls = mtg_urls[(mtg_urls["tonga"] == True)]["print_url"].tolist()
news_raw = mtg.scrape_urls(news_urls, "field__items", speed_up=True)

news_info = []
for raw in news_raw:
    url = raw[0]
    if len(raw[1]) > 1:
        news = raw[1][1].text
    elif len(raw[1]) == 1:
        news = raw[1][0].text
    news_info.append([url, news])

news_df = pd.DataFrame(news_info, columns=["print_url", "news"])
news_df = (news_df.merge(mtg_urls, how="left", on="print_url"))
news_df = news_df[["url", "date", "title", "news", "tag"]]
if not SCRAPE_ALL:
    news_df = (pd.concat([previous_news_df, news_df], axis=0)
                 .reset_index(drop=True))
    news_df["date"] = pd.to_datetime(news_df["date"])
    news_df.to_csv(target_dir+"matangi_news.csv", encoding="utf-8")
else:
    news_df["date"] = pd.to_datetime(news_df["date"])
    news_df.to_csv(target_dir+"matangi_news.csv", encoding="utf-8")