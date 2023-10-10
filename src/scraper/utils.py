import os
import urllib3
import pandas as pd
import numpy as np
import json
from pycookiecheat import chrome_cookies

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
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36",
        "sec-ch-ua-platform":
        "MacOS",
        "upgrade-insecure-requests": "1",
        "dnt": "1",
        "sec-ch-ua":
        '"Not.A/Brand";v="24", "Chromium";v="116", "Google Chrome";v="116"',
        "Accept":
        "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7"
    }

    return headers, 

def configure_cookies(host_url: str, cookies_path: str) -> dict:
      
    cookies = chrome_cookies(host_url, cookies_path)
    return cookies