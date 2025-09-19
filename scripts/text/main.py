import os
from src.text.scrapers.newspapers.solomon_islands import sibc
os.environ["DATA_FOLDER_PATH"] = "data"


if __name__ == "__main__":
    sibc.SIBCScraper().run_full_scrape()
    