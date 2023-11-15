import sys
sys.path.insert(0, "../../")
import pandas as pd
import os
import csv
import time
from datetime import datetime
from src.scraper.scrape import *

search_urls = [
    f"https://www.dailypost.vu/search/?f=html&s=start_time&sd=desc&l=100&t=article&nsa=eedition&app%5B0%5D=editorial&o={num}"
    for num in range(0, 43200, 100)]
target_dir = sys.path[0] + "data/text/vanuatu/"
if not os.path.exists(target_dir):
    os.mkdir(target_dir)

dp = WebScraper(parser="html.parser")
urls_raw = dp.scrape_urls(search_urls, ["card-headline", "card-meta"], speed_up=True)

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
urls_df["url"] = ["https://www.dailypost.vu" + i for i in urls_df.url]
urls_df.to_csv(target_dir + "daily_post_urls.csv", encoding="utf-8")

# Read the urls_df
urls_df = pd.read_csv(target_dir + "daily_post_urls.csv").drop("Unnamed: 0", axis=1)
urls_df = (urls_df[urls_df.url.str.startswith("https://www.dailypost.vu/news/")]
            .reset_index(drop=True))

## Set up Chromedriver
chromedriver_path = sys.path[0] + "scripts/chromedriver"
filepath = target_dir + "daily_posts_news.csv" 
with open(filepath, "w+", encoding="utf-8") as file:
    writer = csv.writer(file)
    writer.writerow(["url", "news"])

dp_news = []
scraper = SeleniumScraper(chromedriver_path)
scraper.start_driver()
with tqdm(total=len(urls_df)) as pbar:
    for idx, url in enumerate(urls_df.url):
        if idx % 5 == 0:
            scraper.driver.delete_all_cookies()
        elements = scraper.scrape_page(url, "//div[@class='asset-body']//p")
        if elements is not None: 
            text = "".join(elem.text for elem in elements)
        else:
            text = "Missing"
        dp_news.append([idx, url, text])

        if idx % 100 == 0:
            with open(filepath, "a", encoding="utf-8") as file:
                writer = csv.writer(file)
                writer.writerows(dp_news)
        dp_news = []
        time.sleep(5)
        pbar.update(1)

news_df = pd.read_csv(filepath).drop("Unnamed: 0", axis=1)
news_df["news_length"] = news_df["news"].apply(lambda x: len(x))
news_df = (news_df[news_df["news_length"] >= np.percentile(news_df["news_length"], 1)]
           .reset_index(drop=True)
           .drop("news_length", axis=1))
news_df = news_df.merge(urls_df, how="left", on="url")
news_df["date"] = pd.to_datetime(news_df["date"])
news_df = news_df[["url", "title", "date", "news"]]
news_df = (news_df[(~news_df.title.str.startswith("Re:")) & 
                  (~news_df.url.str.startswith("https://www.dailypost.vu/news/letters/"))]
                  .sort_values(by="date", ascending=True)
                  .reset_index(drop=True))
news_df.to_csv(filepath, encoding="utf-8")