import os
import sys
from ..config import PROJECT_FOLDER_PATH, SIBC_PAGE_URLS, SCRAPE_ALL
sys.path.insert(0, PROJECT_FOLDER_PATH)
import pandas as pd
import numpy as np
from src.scraper.scrape import WebScraper

target_dir = sys.path[0] + "data/text/solomon_islands/"


