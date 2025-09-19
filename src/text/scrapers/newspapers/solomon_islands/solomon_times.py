import sys
from ..config import PROJECT_FOLDER_PATH, SOLOMON_TIMES_URLS, SCRAPE_ALL
sys.path.insert(0, PROJECT_FOLDER_PATH)
import pandas as pd
from src.scrapers import RequestsScraper

target_dir = sys.path[0] + "data/text/solomon_islands/"

scraper = RequestsScraper("html.parser")
pages_raw = scraper.scrape_urls(SOLOMON_TIMES_URLS, 
                                ["article-list-item"], 
                                speed_up=True)

urls_info = []
for page in pages_raw:
    if len(page[1]) != 0:
        date = "-".join(i for i in page[0].split("/")[-2:])
        for i in page[1][0]:
            url = (i.find("a")["href"])
            title = (i.find("h2").text)
            urls_info.append([url, title, date])

urls_info_df = pd.DataFrame(urls_info, columns=["url", "title", "date"])
urls_info_df["url"] = urls_info_df["url"].apply(lambda x: f"https://www.solomontimes.com{x}")
urls_info_df["date"] = pd.to_datetime(urls_info_df["date"], format="mixed")
urls_info_df.to_csv(target_dir + "solomon_times_urls.csv", encoding="utf-8")


previous_news_df = pd.read_csv(target_dir + 'solomon_times_news.csv').drop("Unnamed: 0", axis=1)
previous_news_df["date"] = pd.to_datetime(previous_news_df["date"], format="mixed")
if not SCRAPE_ALL:
    previous_urls = set(previous_news_df["url"])
    current_urls = set(urls_info_df["url"])
    news_urls = list(current_urls - previous_urls)
else:
    news_urls = urls_info_df["url"].tolist()

news_raw = scraper.scrape_urls(news_urls,
                               ["article-timestamp", "article-body", "tags"],
                   speed_up=True)
news_info = []
for i in news_raw:
    url = i[0]
    for (date, content, tag) in zip(*i[1]):
        date = (date.find("span")["datetime"])
        text = (content.text.strip())
        tags = tag.find_all("a")
        tags_text = " ".join(t.text + "," if i < len(tags) - 1 else t.text
                    for i, t in enumerate(tags))
        news_info.append([url, date, text, tags_text])

news_df = pd.DataFrame(news_info, columns=["url", "date", "news", "tag"])
news_df["date"] = pd.to_datetime(news_df["date"], format="mixed")
if not SCRAPE_ALL:
    current_news_df = pd.concat([news_df, previous_news_df], axis=0)
    current_news_df = (current_news_df.sort_values(by="date", ascending=False)
                       .reset_index(drop=True))
    current_news_df.to_csv(target_dir + 'solomon_times_news.csv', encoding="utf-8")
else:
    news_df.to_csv(target_dir + 'solomon_times_news.csv', encoding="utf-8")


