from src.scraper.scrape import *
import pandas as pd
import os
import sys
sys.path.insert(0, "../../")

target_dir = sys.path[0] + "data/text/png/"
host_url = "https://www.pngbusinessnews.com/"
news_urls = [host_url + f"articles?page={i}" for i in range(1, 93)]

pngb = WebScraper("html.parser")
news_urls_raw = pngb.scrape_urls(
    news_urls, "cell small-12 medium-6 large-6", speed_up=True)

news_info = []
for page in news_urls_raw:
    page_content = page[1]
    for i in page_content:
        url = i.find("a")["href"]
        title = i.find("h3").text
        date = i.find(class_="tag publish-date").text.strip()
        news_info.append([url, date, title])

urls_df = pd.DataFrame(news_info, columns=["url", "date", "title"])
urls_df["date"] = pd.to_datetime(urls_df["date"])
urls_df.to_csv(target_dir+"png_business_urls.csv", encoding="utf-8")

# Re-read the
urls_df = pd.read_csv(target_dir+"png_business_urls.csv")
urls_to_scrape = urls_df.url.tolist()

# content div class_  grid-x margin-bottom-1 article-content
news_contents = pngb.scrape_urls(
    urls_to_scrape, "grid-x margin-bottom-1 article-content", True)

## Create a list to contain [url, news] for each entry
news_list = []
for i in news_contents:
    url = i[0]
    news = i[1][0].text
    news_list.append([url, news])

pngb_news = pd.DataFrame(news_list, columns=["url", "news"])
pngb_news = pngb_news.merge(urls_df, how="left", on="url")
pngb_news = (pngb_news[["url", "date", "title", "news"]]
                .sort_values(by="date")
                .reset_index(drop=True))
pngb_news.to_csv(target_dir + "png_business_news.csv", encoding="utf-8")