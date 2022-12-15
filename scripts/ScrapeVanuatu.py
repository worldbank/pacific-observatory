#!/usr/bin/env python
# coding: utf-8
import os
import pandas as pd
import urllib3
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from scripts.SupportFunc import download_files

# Initialize the webdriver and config
chrome_options = webdriver.ChromeOptions()
prefs = {'download.default_directory': os.getcwd() + '/data/vanuatu'}
chrome_options.add_experimental_option('prefs', prefs)
driver = webdriver.Chrome(os.getcwd() + "/scripts/chromedriver",
                          chrome_options=chrome_options)

# Load the Vanuatu Tourism Archive
driver.get("https://vnso.gov.vu/index.php/en/statistics-by-topic/tourism#archive")

# Find all the available urls for download
downloads = WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.XPATH, "//td/a")))

# Store all file urls in the list
download_urls = list()
for download in downloads:
    url = download.get_attribute("href")
    if ".pdf" in url:
        download_urls.append(url)
    else:
        print(url)



for url in download_urls:
    path = os.getcwd() + "/data/vanuatu/" + url.split("/")[-1]
    download_files(url, path=path)
