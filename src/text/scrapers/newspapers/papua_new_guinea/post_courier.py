import sys
from ..config import (PROJECT_FOLDER_PATH, POST_COURIER_PAGE_URLS, 
                      POST_COURIER_NEWS_ELEMENTS, POST_COURIER_PAGE_ELEMENTS, SCRAPE_ALL)
sys.path.insert(0, PROJECT_FOLDER_PATH)
import pandas as pd
from src.scrapers import RequestsScraper

target_folder = sys.path[0] + "data/text/papua_new_guinea/"

## Initialize the Scraper
scraper = RequestsScraper('html.parser')
pages_raw = scraper.scrape_urls(POST_COURIER_PAGE_URLS,
                                POST_COURIER_PAGE_ELEMENTS,
                                speed_up=True)

urls_info = []
for page in pages_raw:
    page_info = page[1]
    if len(page_info[0]) > 10:
        zipped = zip(page_info[0][:10], page_info[1][:10])
    else:
        zipped = zip(*page_info)
    for title_entry, date_entry in zipped:
        url = title_entry.find("a").attrs["href"]
        title = title_entry.text if title_entry.text is not None else "Missing"
        date_elem = date_entry.find(class_="entry-date published")
        if date_elem is not None:
            date = date_elem.text
        else:
            date = date_entry.text
        urls_info.append([url, title, date])

news_urls = pd.DataFrame(urls_info, columns=["url", "title", "date"])
news_urls["date"] = pd.to_datetime(news_urls["date"], format="mixed")
news_urls = (news_urls.sort_values(by="date", ascending=False)
                .drop_duplicates()
                .reset_index(drop=True))
news_urls.to_csv(target_folder + "post_courier_urls.csv", encoding="utf-8")

if not SCRAPE_ALL: 
    current_news = pd.read_csv(target_folder + "post_courier_news.csv").drop("Unnamed: 0", axis=1)
    current_news["date"] = pd.to_datetime(current_news["date"])
    latest_date = current_news.date.max()
    urls_to_scrape = news_urls[news_urls.date > latest_date]["url"].tolist()
else:
   urls_to_scrape = news_urls["url"].tolist()

news_raw = scraper.scrape_urls(urls_to_scrape, 
                               POST_COURIER_NEWS_ELEMENTS,
                               speed_up=True)
scraped_news = []
for i in news_raw:
    url = i[0]
    for page, tag in zip(*i[1]):
        content = " ".join(p.text for p in page.find_all("p"))
        tags = tag.text if tag is not None else "No Tag"
        scraped_news.append([url, content, tags])

news_df = pd.DataFrame(scraped_news, columns=["url", "news", "tag"])
news_df = news_df.merge(news_urls, how="left", on="url")
if not SCRAPE_ALL:
    news_df = pd.concat([news_df, current_news], axis=0)
    news_df = news_df.sort_values(by="date", ascending=False).reset_index(drop=True)
    news_df.to_csv(target_folder + "post_courier_news.csv", encoding="utf-8")
else:
    news_df.to_csv(target_folder + "post_courier_news.csv", encoding="utf-8")