import os
os.chdir("../../../")
from src.scraper.scrape import *

# Set up
target_dir = os.getcwd() + "/data/text/rnz/"
if not os.path.exists(target_dir):
    os.mkdir(target_dir)

host_url = "https://www.rnz.co.nz"
countries = ["Papua New Guinea", "Fiji", "Samoa"]

for country in countries:
    filename = country.replace(" ", "_").lower() + "_rnz_urls.csv"
    country_base_url = host_url + "/tags/" + str(country) + "?page="
    country_urls = [country_base_url + str(i) for i in range(1, 500)]

    scraper = WebScraper(parser="html.parser")
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
    rnz_df["url"] = [host_url + str(url) for url in rnz_df.url]

    # Save url files
    rnz_df.to_csv(target_dir + filename, encoding="utf-8")

for country in countries:
    country_filepath = target_dir + country.lower().replace(" ", "_") + \
        "_rnz_urls.csv"
    df = pd.read_csv(country_filepath).drop("Unnamed: 0", axis=1)
    news_urls = df[df.news == True]["url"].tolist()
    scraper = WebScraper(parser="html.parser")
    nested_data = scraper.scrape_urls(news_urls, "article__body", speed_up=True)

    news_output = []
    for url, i in nested_data:
        try:
            text = "".join(p.text for p in i[0].find_all("p"))
            news_output.append([url, text])
        except Exception as e:
            print(f"An Error has occured: {e}.")
            news_output.append([url, np.NAN])

    country_news_df = pd.DataFrame(news_output, columns=["url", "news"])
    news_filepath = target_dir + country.lower().replace(" ", "_") + \
        "_rnz_news.csv"
    country_news_df.to_csv(news_filepath, encoding="utf-8")
