import os
os.chdir("../../")
import pandas as pd
import json
from src.scraper.scrape import WebScraper

## Set up 
target_dir = os.getcwd() + "/data/text/abc_au/"
if not os.path.exists(target_dir):
    os.mkdir(target_dir)

def scrape_ajax_abc(document_id: int,
                    size: int = 1000,
                    offset: int = 0
                    ) -> list:

    scraper = WebScraper()
    output = []

    total = 5000
    while offset < total:
        ajax_url = f"https://www.abc.net.au/news-web/api/loader/topicstories?name=PaginationArticles&documentId={document_id}&offset={offset}&size={size}"
        content = scraper.request_url(ajax_url, timeout=30)
        data = json.loads(content)
        total = data["pagination"]["total"]
        for i in data["collection"]:
            link = i["link"]["to"]
            title = i["title"]["children"]
            date = i["timestamp"]["dates"]["firstPublished"]
            media_type = i["contentUri"].split("//")[-1].split("/")[0]
            output.append([link, title, date, media_type])
        offset += size
    return output

topic_dict = {
    # 26514 : "fiji",
    26790 : "solomon_islands",
    26730 : "papua_new_guinea",
    26874 : "vanuatu",
    26720 : "pacific",
    26664 : "marshall_islands",
    26832 : "tonga"

}

for key, name in topic_dict.items():
    output = scrape_ajax_abc(
        document_id = key
    )
    df = (pd.DataFrame(output, columns=["url", "title", "date", "media_type"])
            .drop_duplicates())
    df["url"] = ["https://www.abc.net.au" + i for i in df.url]
    df.to_csv(target_dir + name + "_abc_urls.csv", encoding="utf-8")



for _, name in topic_dict.items():    
    scraper = WebScraper(parser="html.parser")
    df = pd.read_csv(target_dir + name + "_abc_urls.csv").drop("Unnamed: 0", axis=1)
    urls = df[df.media_type == "article"]["url"].tolist()
    expressions = [['RelatedTopics_topicsListItem__mup9a', 'paragraph_paragraph__3Hrfa'] 
                for _ in range(len(urls))]
    print(f"{name}'s scraping work has started.")
    news_output = scraper.scrape_urls(urls, expressions, speed_up=True)
    news_list = []
    for i in news_output:
        url = i[0]
        if len(i[1]) != 0: 
            tags = ''.join(j.text + ", " for j in i[1][0])
            news = ''.join(j.text for j in i[1][1])
        news_list.append([url, news, tags])

    news_df = pd.DataFrame(news_list, columns=["url", "news", "tags"])
    news_df.to_csv(target_dir + name + "_abc_news.csv", encoding="utf-8")