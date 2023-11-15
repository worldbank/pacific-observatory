import os
import sys
sys.path.insert(0, "../../")
import pandas as pd
from src.scraper.scrape import WebScraper

target_dir = sys.path[0] + "data/text/tonga/"
if not os.path.exists(target_dir):
    os.mkdir(target_dir)

search_urls = [f"https://matangitonga.to/topic/all?page={num}"
               for num in range(1, 932)]
mtg = WebScraper("html.parser")
urls_raw = mtg.scrape_urls(search_urls, ["views-field views-field-title",
                                         "views-field views-field-term-node-tid",
                                         "views-field views-field-field-first-publication",
                                         "views-field views-field-field-location"],
                           speed_up=True)
urls_info =  {
    "url" : [],
    "date": [],
    "title" : [],
    "tag": [],
    "location": []
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
news_urls = mtg_urls[mtg_urls.location.str.contains("Tonga")]["url"].tolist()
news_raw = mtg.scrape_urls(news_urls[:10], "field__items", speed_up=True)
