import pandas as pd
import os
import sys
sys.path.insert(0, "../../")
from src.scraper.scrape import *

# Specify the host and saving directory
host_url = "https://fijisun.com.fj/"
fs_urls = [host_url + "category/fiji-news/page/" + str(i)
           for i in range(1, 1546)]
target_dir = sys.path[0] + "data/text/fiji/"

if not os.path.exists(target_dir):
    os.mkdir(target_dir)

# Scrape news URLs
fs = WebScraper(parser="html.parser")
fs_news_urls_raw = fs.scrape_urls(fs_urls,
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
news_info_df.to_csv(target_dir+"fiji_sun_urls.csv", encoding="utf-8")

# Scrape News, Dates and Tags
news_info_df = pd.read_csv(target_dir+"fiji_sun_urls.csv")
news_urls = news_info_df.url.tolist()
news_raw = fs.scrape_urls(news_urls, ["shortcode-content", "tag-block"],  True)
news_content = []
for i in news_raw:
    url = i[0]
    if len(i[1]) != 0:
        text = i[1][0][0].text
        if len(i[1][1]) > 0:
            tags = ",".join(tag.text for tag in i[1][1][0].find_all("a"))    
        else:
            tags = "Missing"
    else:
        tags = "Missing"
        text = "Missing"
    news_content.append([url, text, tags])

news = pd.DataFrame(news_content, columns=["url", "news", "tags"])
news["date"] = news["url"].apply(lambda x: "-".join(x.split("/")[3:6]))
news["not_full"] = news["news"].str.contains("https://eedition.fijisun.com.fj/subscriptionplans")
news.to_csv(target_dir+"fiji_sun_news.csv", encoding="utf-8")