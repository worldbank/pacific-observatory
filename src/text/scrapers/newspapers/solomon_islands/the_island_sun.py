'''
To bypass the Cloudflare authentication, one needs to
1. Import `configure_cookies` and `configure_headers` from src.scraper.utils. 
    a. It might necessary to change the header accordingly, e.g. if you are using
    Chrome v 119.0.0.0, you might need to change the header in compatiable with your 
    system;
    b. To call `configure_cookies`, you need to manually using your browser to access 
    https://theislandsun.com.sb/, which you will probably go through the cloundflare 
    verification. Be sure to go through the process and store all cookies. (You can find 
the relevant cookies by (right-click) Inspect -> Application -> Cookies -> 
    https://theislandsun.com.sb, and `cf_clearance` is the cookies that mostly help us bypass
    the cloudflare authentication).
2. Insert `domain` and `cookies_path` args when initializing the RequestsScraper class, and the 
default `cookies_path` on MacOS should be `/Users/czhang/Library/Application Support/Google/Chrome/Profile/Cookies`.
3. Make sure that you refresh the https://theislandsun.com.sb periodically (~ every 20mins), becasue
~ 30 minutes the cookies would expire and one needs to manually go through cloudflare verification as 
describe in 1.b.
See more in pycookiecheat.
'''

import os
import sys
from ..config import PROJECT_FOLDER_PATH, SCRAPE_ALL, TIS_PAGE_URLS, COOKIES_PATH
sys.path.insert(0, PROJECT_FOLDER_PATH)
import pandas as pd
import numpy as np
from src.scraper.scrape import RequestsScraper
from src.scraper.utils import configure_cookies, configure_headers

target_dir = sys.path[0] + "data/text/solomon_islands/"

headers = configure_headers()
scraper = RequestsScraper(
    "html.parser",
    headers=headers,
    domain="https://theislandsun.com.sb/",
    cookies_path=COOKIES_PATH
)

pages_raw = scraper.scrape_urls(TIS_PAGE_URLS, "item-details",
                                speed_up=True)
news_info = []
for page in pages_raw:
    for ele in page[1]:
        title_entry = ele.find(class_="entry-title td-module-title")
        tag_entry = ele.find(class_="td-post-category")
        url_entry = title_entry.find("a")
        date_entry = ele.find(class_="td-post-date")
        if ele is not None:
            news_info.append([title_entry.text, url_entry["href"], date_entry.text, tag_entry.text])

urls_df = pd.DataFrame(news_info, columns=["title", "url", "date", "tag"])
urls_df["date"] = pd.to_datetime(urls_df["date"], format="mixed")
urls_df = urls_df.sort_values(by="date", ascending=False).reset_index(drop=True)
urls_df.to_csv(target_dir + "island_sun_urls.csv", encoding="utf-8")


previous_news_df = pd.read_csv(
    target_dir + "island_sun_news.csv").drop("Unnamed: 0", axis=1)
previous_news_df["date"] = pd.to_datetime(
    previous_news_df["date"], format="mixed")
if not SCRAPE_ALL:
    previous_urls = set(previous_news_df["url"])
    current_urls = set(urls_df["url"])
    urls_to_scrape = list(current_urls - previous_urls)
else:
    urls_to_scrape = urls_df["url"].tolist()

news_raw = scraper.scrape_urls(
    urls_to_scrape, "td-post-content tagdiv-type", speed_up=True)

news_info = []
for i in news_raw:
    url = i[0]
    if len(i[1]) > 0:
        text = " ".join(p.text for p in i[1][0].find_all("p"))
    else:
        text = "Missing"
    news_info.append([url, text])

news_df = pd.DataFrame(news_info, columns=["url", "news"])
news_df = news_df.merge(urls_df, how="left", on="url")

if not SCRAPE_ALL:
    current_news_df = pd.concat([news_df, previous_news_df], axis=0)
    current_news_df = (current_news_df.sort_values(by="date", ascending=False)
                            .reset_index(drop=True))
    current_news_df.to_csv(target_dir + "island_sun_news.csv", encoding="utf-8")
else:
    news_df.to_csv(target_dir + "island_sun_news.csv", encoding="utf-8")  