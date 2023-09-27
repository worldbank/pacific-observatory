import os
os.chdir("../../")
import json
from src.scraper.scrape import *

scraper = WebScraper(
    url=
    "https://www.theguardian.com/world/2023/aug/12/between-two-worlds-life-of-png-tribe-leader-and-plantation-owner-honoured",
    parser="xpath")
scraper.load_page()
scraper.parse_page()

print(scraper.parsed_content)