import os
import sys
sys.path.insert(0, "../../")
import pandas as pd
import json
import requests
from tqdm import tqdm
import multiprocessing
from concurrent.futures import ThreadPoolExecutor, as_completed
from src.scraper.scrape import WebScraper

target_dir = sys.path[0] + "data/text/samoa/"
if not os.path.exists(target_dir):
    os.mkdir(target_dir)

def load_page(url, timeout=30):
    try:
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()
        output = json.loads(response.content)
        return output
    except requests.exceptions.RequestException as e:
        print(f"Failed to retrieve the page: {e}")
        pass

urls = [f"https://www.samoaobserver.ws/stories/page/{num}.json?&category=samoa&api=true"
        for num in range(0, 2079)]
scraped_data = []
with tqdm(total=len(urls)) as pbar:
    max_workers = multiprocessing.cpu_count() + 4
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_url = {executor.submit(load_page, url): (url) for url in urls}
        for future in as_completed(future_to_url):
            url = future_to_url[future]
            try:
                data = future.result()
            except Exception as exc:
                print('%r generated an exception: %s' % (url, exc))
            else:
                scraped_data.append([url, data])
                pbar.update(1)

url_output = []
for page in scraped_data:
    request_url = page[0]
    json_data = page[1]["stories"]
    for i in json_data:
        url_output.append([i["id"], i["heading"], i["published_date"], i["is_premium"]])

so_urls = pd.DataFrame(url_output, columns=["id", "title", "date", "is_premium"])
so_urls["date"] = pd.to_datetime(so_urls["date"])
so_urls = so_urls.sort_values(by="date", ascending=True).reset_index(drop=True)
so_urls["url"] = so_urls["id"].apply(lambda x: f"https://www.samoaobserver.ws/category/samoa/{x}")
so_urls.to_csv(target_dir+"samoa_observer_urls.csv", encoding="utf-8")

## Scrape News with non-subscription-needed urls
so_urls = pd.read_csv(target_dir+"samoa_observer_urls.csv").drop("Unnamed: 0", axis=1)
so_urls_to_scrape = so_urls[so_urls.is_premium == False]['url'].tolist()
so = WebScraper("html.parser")
so_raw = so.scrape_urls(so_urls_to_scrape, 
              "article__content text-new-brand-black py-0 leading-big",
              speed_up=True)

so_news = []
for i in so_raw:
    url = i[0]
    if i[1]:  
        news = "".join(p.text for p in i[1][0].find_all("p"))
    else:
        news = "Missing"
    so_news.append([url, news])

so_news_df = pd.DataFrame(so_news, columns=["url", "news"])
for idx in so_news_df[so_news_df.news == "Missing"].index:
    url = so_news_df["url"][idx]
    raw = so.scrape_url(url, 
                        "article__content text-new-brand-black py-0 leading-big")
    news = "".join(p.text for p in raw[0].find_all("p"))
    so_news_df.iloc[idx, 1] = news
    
so_news_df = so_news_df.merge(so_urls, how="left", on="url")
so_news_df = so_news_df[["url", "title", "date", "news"]]
so_news_df.to_csv(target_dir+"samoa_observer_news.csv", encoding="utf-8")