import os
import urllib3
import pandas as pd
import numpy as np
import json
import re
from pycookiecheat import chrome_cookies
from dateutil.parser import parse
from datetime import datetime, timedelta
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

# Wrap the urllib3 downloading functions
def download_files(url: str, path: str, chunk_size=1024):
    """
    Args
    ------
    url: string
        The string of URL for downloading.
    path: string
        The string of the saving path.
    chuck_sise: int
        The default is set as 1024.

    Return
    ------
        N/A
    """

    http = urllib3.PoolManager()
    r = http.request(
        'GET',
        url,
        preload_content=False)

    with open(path, 'wb') as out:
        while True:
            data = r.read(chunk_size)
            if not data:
                break
            out.write(data)
    r.release_conn()

def configure_headers():

    headers = {
        "User-Agent":
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Sec-Ch-Ua-Platform":
        "MacOS",
        "upgrade-insecure-requests": "1",
        "dnt": "1",
        "Sec-Ch-Ua":
        '"Google Chrome";v="120", "Not;A=Brand";v="8", "Chromium";v="120"',
        "Accept":
        "*/*",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Accept-Language": "en-US,en;q=0.9",
        "Accpet-Encoding": "gzip, deflate, br",
    }

    return headers 

def configure_cookies(host_url: str, cookies_path: str) -> dict:
      
    cookies = chrome_cookies(host_url, cookies_path)
    return cookies

def check_latest_date(filepath: str):
    df = pd.read_csv(filepath)
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"], format="mixed")
        return df["date"].max()
    

def handle_mixed_dates(date: str, pattern="\d+"):
    try:
        date = parse(date)
    except:
        if "ago" in date:
            now = datetime.now()
            number = int(re.findall(pattern, date)[0])
            if "min" in date:
                date = now - timedelta(minutes=number)
            elif "hr" in date or "hour" in date:
                date = now - timedelta(hours=number)
    finally:
        return date
            
            