import sys
import os
sys.path.insert(0, "/Users/czhang/Desktop/pacific-observatory/")
import pandas as pd
from src.scraper.scrape import SeleniumScraper, RequestsScraper

target_dir = sys.path[0] + "data/text/vanuatu/"
output_path = target_dir + "vbr_news.csv"


page_urls = [f"https://vbr.vu/category/news/page/{num}" for num in range(1,61)]
vbr = RequestsScraper("html.parser")
urls_raw = vbr.scrape_urls(page_urls, "post has-thumbnail", speed_up=True)

urls_info = {
    "url": [], 
    "date": [], 
    "title": [], 
}
for page in urls_raw:
    url = page[0]
    info = page[1]
    titles = [i.find("h2").text.strip() for i in info]
    urls = [i.find("a")["href"] for i in info]
    dates = [i.find(class_="post-info").text.split("|")[0].strip()
             for i in info]
    urls_info["url"].extend(urls)
    urls_info["title"].extend(titles)
    urls_info["date"].extend(dates)

vbr_urls = pd.DataFrame(urls_info)
vbr_urls["date"] = pd.to_datetime(vbr_urls["date"])
vbr_urls.to_csv(target_dir + "vbr_urls.csv", encoding="utf-8")

news_urls = vbr_urls["url"].tolist()
news_info = vbr.scrape_urls(news_urls, "post", speed_up=True)

vbr_news = []
for info in news_info:
    url = info[0]
    news_raw = info[1][0]
    news = "".join(p.text for p in news_raw.find_all("p")[1:])
    vbr_news.append([url, news])

vbr_news_df = pd.DataFrame(vbr_news, columns=["url", "news"])
vbr_news_df = vbr_news_df.merge(vbr_urls, how="left", on="url")
vbr_news_df = vbr_news_df[["url", "date", "title", "news"]]
vbr_news_df.to_csv(f"{target_dir}/vbr_news.csv", encoding="utf-8")

