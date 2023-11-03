import os
os.chdir("../")
import pandas as pd
import urllib3
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from SupportFunc import download_files

#
solomon_url = "https://www.statistics.gov.sb/statistics/visitor-arrivals"
download_xpath = "//a[@class= 'afl_download']"
download_folder = os.getcwd() + "/data/tourism/solomon/"


# Intiate the driver
driver = webdriver.Chrome("./scripts/chromedriver")
driver.get(solomon_url)

# Find all downloadable files elements by Xpath
file_elems = WebDriverWait(driver, 5).until(
        EC.presence_of_all_elements_located((By.XPATH, download_xpath)))

download_dict = {"filename": [], "url": []}
for filepath in file_elems:
    download_dict["filename"].append(filepath.get_attribute("text"))
    download_dict["url"].append(filepath.get_attribute("href"))

# Backup the scrpaed urls for potential usage
url_backup = pd.DataFrame(download_dict)
url_backup.to_csv(download_folder + "url_backup.csv", encoding="utf-8")

# Download all available files
for idx, val in enumerate(download_dict["url"]):
    path = download_folder + download_dict["filename"][idx] + ".pdf"
    download_files(val, path=path)
