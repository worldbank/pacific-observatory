import os
import pandas as pd
import urllib3
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from scripts.python.utils import download_files


# Config the chromedriver
chrome_options = webdriver.ChromeOptions()
prefs = {'download.default_directory': os.getcwd() + '/data/tourism/fiji'}
chrome_options.add_experimental_option('prefs', prefs)
driver = webdriver.Chrome(os.getcwd() + "/scripts/chromedriver",
                          chrome_options=chrome_options)


start = 0
download_urls, page_lst = list(), list()
while start < 136:

    url = "https://www.statsfiji.gov.fj/latest-releases/tourism-and-migration/visitor-arrivals.html?start=" + \
        str(start)
    driver.get(url)

    try:
        pdf_elem = WebDriverWait(driver, 5).until(
            EC.presence_of_all_elements_located((By.XPATH, "//p/embed")))
        if len(pdf_elem) == 1:
            pdf_url = pdf_elem[0].get_attribute("src")
            download_urls.append(pdf_url)
            start += 1

    except:
        print("Page", str(start), "might not contain a pdf file.")
        page_lst.append(url)
        start += 1

# Download pdf files
for url in download_urls:
    path = os.getcwd() + "/data/tourism/fiji/scraping/updated/" + url.split("/")[-1]
    download_files(url, path=path)
