import sys
from ..config import PROJECT_FOLDER_PATH, PINA_URLS, SCRAPE_ALL
sys.path.insert(0, PROJECT_FOLDER_PATH)
import pandas as pd
from src.scrapers import RequestsScraper

# PINA
PINA_URLS = [f"https://pina.com.fj/category/news/page/{num}"
             for num in range(1, 475)]

target_dir = sys.path[0] + "data/text/pacific/"

scraper = RequestsScraper("html.parser")
pages_raw = scraper.scrape_urls(PINA_URLS,
                                ["td_module_10 td_module_wrap td-animation-stack"],
                                speed_up=True)
urls_info = []
for page in pages_raw:
    items = page[1][0]
    for i in items:
        title = (i.find("h3").text)
        url = i.find("a")["href"]
        date = i.find(class_="td-post-date").text
        tag = i.find(class_="td-post-category").text
        urls_info.append([url, title, date])

urls_df = pd.DataFrame(urls_info, columns=["url", "title", "date"])
urls_df["date"] = pd.to_datetime(urls_df["date"], format="mixed")
urls_df = (urls_df.sort_values(by="date", ascending=False)
           .reset_index(drop=True))
urls_df.to_csv(target_dir + "pac_after_2020_urls.csv", encoding="utf-8")


previous_news_df = (pd.read_csv(target_dir + "pac_news_after_2020.csv")
                    .drop("Unnamed: 0", axis=1))
previous_news_df["date"] = pd.to_datetime(
    previous_news_df["date"], format="mixed")
if not SCRAPE_ALL:
    previous_urls = set(previous_news_df["url"])
    current_urls = set(urls_df["url"])
    urls_to_scrape = list(current_urls - previous_urls)
else:
    urls_to_scrape = urls_df["url"].tolist()

news_raw = scraper.scrape_urls(urls_to_scrape,
                               ["td-post-content tagdiv-type", "td-post-source-tags"],
                               speed_up=True)

news_list = []
for i in news_raw:
    url = i[0]
    news = "".join(p.text for p in i[1][0][0].find_all("p"))
    tags = "".join(i.text.lower() + " " for i in i[1][1][0].find_all("li")
                   if i.text.lower() != "tags")
    news_list.append([url, news, tags])

news_df = pd.DataFrame(news_list, columns=["url", "news", "tags"])
news_df = news_df.merge(urls_df, how="left", on="url")

if not SCRAPE_ALL:
    news_df = pd.concat([news_df, previous_news_df], axis=0)
    news_df = news_df.sort_values(by="date", ascending=False).reset_index(drop=True)
    news_df.to_csv(target_dir + "pac_after_2020.csv", encoding="utf-8")
else:
    news_df.to_csv(target_dir + "pac_after_2020.csv", encoding="utf-8")


# Additional measures to combine before and after 2020
pac_before = pd.read_csv(
    target_dir + "pac_news_before_2021.csv").drop("Unnamed: 0", axis=1)
pac_before["title"] = pac_before["title"].str.lower().str.strip()
news_df["title"] = news_df["title"].str.lower().str.strip()
duplicated_sets = (
    set(pac_before["title"]).intersection(set(news_df["title"])))
pac_before = pac_before[~pac_before.title.isin(
    duplicated_sets)][["date", "title", "news"]]
pac = pd.concat([pac_before, news_df[["date", "title", "news"]]], axis=0)
pac["date"] = pd.to_datetime(pac["date"])
pac = pac.sort_values(by="date", ascending=False).reset_index(drop=True)
pac.to_csv(target_dir + "pac_news.csv", encoding="utf-8")
