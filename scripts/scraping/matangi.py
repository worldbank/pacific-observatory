import os
import sys
sys.path.insert(0, "/Users/czhang/Desktop/pacific-observatory/")
import pandas as pd
from src.scraper.scrape import WebScraper
from src.scraper.utils import check_latest_date

target_dir = sys.path[0] + "data/text/tonga/"
if not os.path.exists(target_dir):
    os.mkdir(target_dir)

MATANGI_PAGE_URLS = [f"https://matangitonga.to/topic/all?page={num}"
               for num in range(1, 937)]
mtg = WebScraper("html.parser")
urls_raw = mtg.scrape_urls(MATANGI_PAGE_URLS, ["views-field views-field-title",
                                         "views-field views-field-term-node-tid",
                                         "views-field views-field-field-first-publication",
                                         "views-field views-field-field-location"],
                           speed_up=True)
urls_info =  {
    "url" : [],
    "date": [],
    "title" : [],
    "tag": [],
    "location": [],
}
for page in urls_raw:
    page_url, page_raw = page[0], page[1]
    urls_info["title"].extend([i.text for i in page_raw[0]])
    urls_info["url"].extend([i.find("a")["href"] for i in page_raw[0]])
    urls_info["date"].extend([i.text for i in page_raw[2]])
    urls_info["tag"].extend([i.text for i in page_raw[1]])
    urls_info["location"].extend([i.text.strip() for i in page_raw[3]])

mtg_urls = pd.DataFrame(urls_info)
mtg_urls["url"] = [f"https://matangitonga.to{url}" for url in mtg_urls.url]
mtg_urls["date"] = pd.to_datetime(mtg_urls["date"])
mtg_urls.to_csv(f"{target_dir}matangi_urls.csv", encoding="utf-8")

# 
urls_df = pd.read_csv(target_dir+"matangi_urls.csv").drop("Unnamed: 0", axis=1)
urls_df["tonga"] = urls_df["location"].apply(lambda x: "tonga" in str(x).lower())
news_urls = urls_df[urls_df["tonga"] == True]["url"].tolist()
print_urls_raw = mtg.scrape_urls(news_urls, "print-page", speed_up=True)

# Create a mapping between page urls and 
urls_mapping = []
for i in print_urls_raw:
    original_url = i[0]
    print_url = i[1][0]["href"]
    urls_mapping.append([original_url, print_url])
urls_map_df = pd.DataFrame(urls_mapping, columns=["original_url", "print_url"])
urls_map_df.to_csv(f"{target_dir}matangi_urls_map.csv", encoding="utf-8")

print_urls = urls_map_df["print_url"].tolist()
news_raw = mtg.scrape_urls(print_urls, "field__items", speed_up=True)

news_info = []
for raw in news_raw:
    url = raw[0]
    if len(raw[1]) > 1:
        news = raw[1][1].text
    elif len(raw[1]) == 1:
        news = raw[1][0].text
    news_info.append([url, news])

news_df = pd.DataFrame(news_info, columns=["print_url", "news"])
news_df = (news_df.merge(urls_map_df, how="left", on="print_url")
                  .merge(urls_df, how="left", 
                         left_on="original_url", right_on="url"))
news_df = news_df[["url", "date", "title", "news", "tag"]]
news_df.to_csv(target_dir+"matangi_news.csv", encoding="utf-8")