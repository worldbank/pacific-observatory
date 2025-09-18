import os
import sys
from ..config import PROJECT_FOLDER_PATH
sys.path.insert(0, PROJECT_FOLDER_PATH)
import numpy as np
import pandas as pd
from src.scraper.utils import check_latest_date
from src.scraper.scrape import RequestsScraper

# Basic Setup
host_url = "https://www.rnz.co.nz"
countries = ["Solomon Islands", "Samoa", "Fiji", "Papua New Guinea"]
scrape_all = False

for country in countries:
    # Filepath Setup
    url_filepath = country.replace(" ", "_").lower() + "_rnz_urls.csv"
    target_dir = sys.path[0] + "/data/text/" + \
        country.replace(" ", "_").lower() + "/"
    news_filepath = country.lower().replace(" ", "_") + "_rnz_news.csv"

    # Scrping URL Setup
    country_base_url = host_url + "/tags/" + str(country) + "?page="
    country_urls = [country_base_url + str(i) for i in range(1, 500)]

    scraper = RequestsScraper(parser="html.parser")
    data = scraper.scrape_urls(country_urls, "o-digest__detail")

    output = []
    for pg in data:
        for i in pg:
            output.append([i.find("h3").text,
                           i.find("span").text,
                           i.find("a")["href"]])

    rnz_df = pd.DataFrame(
        output, columns=["title", "date", "url"]).drop_duplicates()
    rnz_df["news"] = rnz_df["url"].apply(
        lambda x: x.split("/")[2] != "programmes")
    rnz_df["date"] = pd.to_datetime(rnz_df["date"])

    rnz_df["url"] = [host_url + str(url) for url in rnz_df.url]

    # Save url files
    rnz_df.to_csv(target_dir + url_filepath, encoding="utf-8")

    if not scrape_all:
        latest_scraped_date = check_latest_date(target_dir + news_filepath)
        news_urls = rnz_df[(rnz_df.date > latest_scraped_date) & (
            rnz_df.news == True)]["url"].tolist()
    else:
        news_urls = rnz_df[rnz_df.news == True]["url"].tolist()

    scraper = RequestsScraper(parser="html.parser")
    nested_data = scraper.scrape_urls(
        news_urls, "article__body", speed_up=True)
    news_output = []
    for url, i in nested_data:
        try:
            text = "".join(p.text for p in i[0].find_all("p"))
            news_output.append([url, text])
        except Exception as e:
            print(f"An Error has occured: {e}.")
            news_output.append([url, np.NAN])

    country_news_df = pd.DataFrame(news_output, columns=["url", "news"])
    country_news_df = country_news_df.merge(rnz_df[["url", "date"]], how="left", on="url")
    if not scrape_all:
        previous_news_df = pd.read_csv(
            target_dir + news_filepath).drop("Unnamed: 0", axis=1)
        previous_news_df["date"] = pd.to_datetime(previous_news_df["date"])
        latest_news_df = (pd.concat([previous_news_df, country_news_df], axis=0)
                            .sort_values(by="date", ascending=False)
                            .reset_index(drop=True))
        latest_news_df.to_csv(target_dir + news_filepath, encoding="utf-8")
    else:
        country_news_df.to_csv(target_dir + news_filepath, encoding="utf-8")
