import os
import sys
from .config import PROJECT_FOLDER_PATH, FIJI_SUN_URLS, SCRAPE_ALL
sys.path.insert(0, PROJECT_FOLDER_PATH)
import pandas as pd
import numpy as np
from src.scraper.scrape import WebScraper

SCRAPE_ALL = True

# Specify the host and saving directory
target_dir = sys.path[0] + "data/text/fiji/"

# Scrape news URLs
fs = WebScraper(parser="html.parser")
fs_news_urls_raw = fs.scrape_urls(FIJI_SUN_URLS,
                                  "article-header",
                                  speed_up=True)

# Extract Title and URL from nested lists
news_info = []
for page in fs_news_urls_raw:
    page_raw = page[-1]
    for i in page_raw:
        title = i.text.strip()
        url = i.find("a")["href"]
        news_info.append([title, url])

news_info_df = pd.DataFrame(news_info, columns=["title", "url"])
news_info_df["date"] = news_info_df["url"].apply(lambda x: "-".join(x.split("/")[3:6]))
news_info_df["date"] = pd.to_datetime(news_info_df["date"])
news_info_df = news_info_df.drop_duplicates().reset_index(drop=True)
news_info_df.to_csv(target_dir+"fiji_sun_urls.csv", encoding="utf-8")

# Scrape News, Dates and Tags
previous_news_df = pd.read_csv(target_dir+"fiji_sun_news.csv").drop("Unnamed: 0", axis=1)

if not SCRAPE_ALL:
    previous_urls = set(previous_news_df["url"])
    current_urls = set(news_info_df["url"])
    news_urls = list(current_urls - previous_urls)
else:
    news_urls = news_info_df.url.tolist()
news_raw = fs.scrape_urls(news_urls, ["shortcode-content", "tag-block"],  True)
news_content = []
for i in news_raw:
    url = i[0]
    if len(i[1]) != 0:
        text = " ".join(p.text for p in i[1][0][0].find_all("p"))
        if len(i[1][1]) > 0:
            tags = ", ".join(tag.text for tag in i[1][1][0].find_all("a"))    
        else:
            tags = "Missing"
    else:
        tags = "Missing"
        text = "Missing"
    news_content.append([url, text, tags])

news = pd.DataFrame(news_content, columns=["url", "news", "tags"])
news["date"] = news["url"].apply(lambda x: "-".join(x.split("/")[3:6]))
news["not_full"] = news["news"].str.contains("https://eedition.fijisun.com.fj/subscriptionplans")
if not SCRAPE_ALL:
    news = pd.concat([news, previous_news_df], axis=0)
    news = (news.sort_values(by="date", ascending=False)
                .reset_index(drop=True))
    news.to_csv(target_dir+"fiji_sun_news.csv", encoding="utf-8")
else: 
    news.to_csv(target_dir+"fiji_sun_news.csv", encoding="utf-8")