import sys
from ..config import PROJECT_FOLDER_PATH, SIBC_PAGE_URLS, SCRAPE_ALL
sys.path.insert(0, PROJECT_FOLDER_PATH)
import pandas as pd
from src.scrapers import RequestsScraper

target_dir = sys.path[0] + "data/text/solomon_islands/"

scraper = RequestsScraper("html.parser")
pages_raw = scraper.scrape_urls(SIBC_PAGE_URLS,
                                "item-bot-content",
                                speed_up=True)

# Parse
urls_info = []
for page in pages_raw:
    item = page[1][0]
    title_entry = item.find(class_="item-title").find("a")
    date_entry = item.find(class_="item-date-time")
    date = date_entry.text.replace("-", "").strip()
    urls_info.append([title_entry["href"], title_entry.text, date])

urls_df = pd.DataFrame(urls_info, columns=["url", "title", "date"])
urls_df["date"] = pd.to_datetime(urls_df["date"], format="mixed")
urls_df = urls_df.sort_values(by="date").reset_index(drop=True)
urls_df.to_csv(target_dir + "sibc_urls.csv", encoding="utf-8")


previous_news_df = pd.read_csv(
    target_dir + "sibc_news.csv").drop("Unnamed: 0", axis=1)
previous_news_df["date"] = pd.to_datetime(
    previous_news_df["date"], format="mixed")

if not SCRAPE_ALL:
    previous_urls = set(previous_news_df["url"])
    current_urls = set(urls_df["url"])
    urls_to_scrape = list(current_urls - previous_urls)
else:
    urls_to_scrape = urls_df["url"].tolist()

news_raw = scraper.scrape_urls(urls_to_scrape,
                               ["entry-body", "entry-taxonomies"],
                               speed_up=True)

news_info = []
for news in news_raw:
    url = news[0]
    for news_entry, tag_entry in zip(*news[1]):
        text = " ".join(p.text for p in news_entry.find_all("p"))
        tags = ", ".join(tag.text for tag in tag_entry.find_all("a"))
        news_info.append([url, text, tags])

news_df = pd.DataFrame(news_info, columns=["url", "news", "tag"])
news_df = news_df.merge(urls_df, how="left", on="url")[["url", "title", "date", "news", "tag"]]
if not SCRAPE_ALL:
    current_news_df = pd.concat([news_df, previous_news_df], axis=0)
    current_news_df = (current_news_df.sort_values(by="date", ascending=False)
                        .reset_index(drop=True))
    current_news_df.to_csv(target_dir + "sibc_news.csv", encoding="utf-8")
else:
    news_df.to_csv(target_dir + "sibc_news.csv", encoding="utf-8")
