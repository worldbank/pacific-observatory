import os
import numpy as np
import requests
from bs4 import BeautifulSoup
import urllib
import urllib.request
from tqdm import tqdm

def load_page(url, timeout):
    r = requests.get(url)
    return r.content

def extract_news_info(url, params=None, timeout=5):
    content = load_page(url, timeout)
    soup = BeautifulSoup(content, "html.parser")
    info_dict = {"url": [], "title": [], "date": []}
    if params is None:
        params = {"title_entry": "entry-container",
                  "title": "entry-title",
                  "date": "entry-date"}
    for a in soup.find_all(class_=params["title_entry"]):
        entry_title = a.find(class_=params["title"])
        if params["date"] is not None:
            info_dict["date"].append(a.find(class_=params["date"]).text)
        else:
            info_dict["date"].append(np.NaN)
            
        if entry_title is not None:
            info_dict["url"].append(entry_title.find("a").attrs["href"])
            info_dict["title"].append(entry_title.text)
        else:
            info_dict["url"].append(a.find("a").attrs["href"])
            info_dict["title"].append("Missing Title.")
    return info_dict