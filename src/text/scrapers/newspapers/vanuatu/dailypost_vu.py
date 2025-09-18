import sys
import os
sys.path.insert(0, "/Users/czhang/Desktop/pacific-observatory/")
import pandas as pd
import numpy as np
import csv
import time
from datetime import datetime
from src.scraper.scrape import RequestsScraper, SeleniumScraper
from src.scraper.utils import check_latest_date, handle_mixed_dates
from tqdm import tqdm

scrape_all = False

VU_DAILY_PAGE_URLS = [
    f"https://www.dailypost.vu/search/?f=html&s=start_time&sd=desc&l=100&t=article&nsa=eedition&app%5B0%5D=editorial&o={num}"
    for num in range(0, 43900, 100)]
target_dir = sys.path[0] + "data/text/vanuatu/"
if not os.path.exists(target_dir):
    os.mkdir(target_dir)

dp = RequestsScraper(parser="html.parser")
urls_raw = dp.scrape_urls(VU_DAILY_PAGE_URLS, ["card-headline", "card-meta"], speed_up=True)

urls_info = []
with tqdm(total=len(urls_raw)) as pbar:
    for page in urls_raw:
        cards_raw = page[1]
        titles_raw = cards_raw[0]
        meta = cards_raw[1]
        titles = [i.text.strip() for i in titles_raw]
        urls = [i.find("a")["href"] for i in titles_raw]
        dates = [i.find("time").text for i in meta]
        for title, url, date in zip(titles, urls, dates):
            urls_info.append([title, date, url])
        pbar.update(1)

# Format the columns
urls_df = pd.DataFrame(urls_info, columns=["title", "date", "url"])
urls_df["date"] = pd.to_datetime(urls_df["date"].apply(handle_mixed_dates), format="mixed")
urls_df["url"] = ["https://www.dailypost.vu" + i for i in urls_df.url]
urls_df.to_csv(target_dir + "daily_post_urls.csv", encoding="utf-8")

# Check gaps between scrapings
news_path = target_dir + "daily_posts_news.csv" 
latest_date = check_latest_date(news_path)
previous_news_df = pd.read_csv(news_path).drop("Unnamed: 0", axis=1)
urls_df = (urls_df[(urls_df.url.str.startswith("https://www.dailypost.vu/news/")) & (urls_df.date > latest_date)]
            .reset_index(drop=True))
news_urls = urls_df["url"].tolist()

## Set up Chromedriver
chromedriver_path = sys.path[0] + "scripts/chromedriver"
if scrape_all: 
    with open(news_path, "w+", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["url", "news"])

dp_news = []
scraper = SeleniumScraper(chromedriver_path)
scraper.start_driver()
with tqdm(total=len(news_urls)) as pbar:
    for idx, url in enumerate(news_urls):
        if idx % 5 == 0:
            scraper.driver.delete_all_cookies()
        elements = scraper.scrape_page(url, "//div[@class='asset-body']//p")
        if elements is not None: 
            text = "".join(elem.text for elem in elements)
        else:
            text = "Missing"
        dp_news.append([url, urls_df["title"][idx], urls_df["date"][idx], text])
        
        time.sleep(5)
        pbar.update(1)

# Drop the row that is significantly shorter than others 
previous_news_df = pd.read_csv(news_path).drop("Unnamed: 0", axis=1)
current_news_df = pd.DataFrame(dp_news, columns=["url", "title", "date", "news"])
news_df = pd.concat([previous_news_df, current_news_df], axis=0)
## Potential Issues of constant changing raw data because of np.percentile
news_df["news_length"] = news_df["news"].apply(lambda x: len(x))
news_df = (news_df[news_df["news_length"] >= 50]
           .reset_index(drop=True)
           .drop("news_length", axis=1))
news_df["date"] = pd.to_datetime(news_df["date"], format="mixed")

# Drop 
news_df = (news_df[(~news_df.title.str.startswith("Re:")) & 
                  (~news_df.url.str.startswith("https://www.dailypost.vu/news/letters/"))]
                  .sort_values(by="date", ascending=True)
                  .reset_index(drop=True))
news_df.to_csv(news_path, encoding="utf-8")