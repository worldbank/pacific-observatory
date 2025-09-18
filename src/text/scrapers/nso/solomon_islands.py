import os
import sys
import re
from ..config import PROJECT_FOLDER_PATH
sys.path.insert(0, PROJECT_FOLDER_PATH)
import pandas as pd
from src.scraper.scrape import SeleniumScraper
from src.scraper.utils import download_files

# pre-defined parameters
KEYWORD = "cpi"
sb_nso_url = f"https://statistics.gov.sb/documents/?q={KEYWORD}"
download_xpath = "//a[@class='downloadlink wpfd_downloadlink']"
chromedriver_path = sys.path[0] + "/scripts/chromedriver"
SAVED_PATH = sys.path[0] + "/data/official_statistics/solomon_islands/cpi/"

def scrape_sb_nso(url: str,
                  driver_path: str = chromedriver_path,
                  download_path: str = SAVED_PATH) -> list:
    """
    
    """
    urls = []
    scraper = SeleniumScraper(driver_path=driver_path,
                              download_path=download_path)
    scraper.start_driver()
    scraper.driver.get(sb_nso_url)
    while True:
        try:
            download_elems = scraper.perform_search(download_xpath)
            urls.extend(
                [elem.get_attribute("href") for elem in download_elems])
            next_page_button = scraper.perform_search(
                "//a[@class='next page-numbers']")[0]
            next_page_button.click()
        except:
            break
    return urls

month_mapping = {
    'january': '01',
    'jan': '01',
    'february': '02',
    'feb': '02',
    'march': '03',
    'mar': '03',
    'april': '04',
    'apr': '04',
    'may': '05',
    'june': '06',
    'jun': '06',
    'july': '07',
    'jul': '07',
    'august': '08',
    'aug': '08',
    'september': '09',
    'sep': '09',
    'october': '10',
    'oct': '10',
    'november': '11',
    'nov': '11',
    'december': '12',
    'dec': '12'
}


def parse_file_name(file_name):
    """
    The function is to extract yyyymm from a specific filename.
    """
    regex = r"(?P<month>" + "|".join(
        month_mapping.keys()) + r")(?=[-_\.])(.*?)(?P<year>\d{4})"
    match = re.search(regex, file_name, re.IGNORECASE)
    if match:
        month = match.group("month").lower()
        year = match.group("year")
        month_num = month_mapping[month]
        return f"cpi_{year}_{month_num}"
    else:
        return file_name


cpi_urls = scrape_sb_nso(sb_nso_url)
cpi_urls_df = pd.DataFrame(cpi_urls, columns=["url"])
cpi_urls_df["filename"] = cpi_urls_df["url"].apply(parse_file_name)
cpi_urls_df.to_csv(f"{SAVED_PATH}cpi_urls_backup.csv", encoding="utf-8")

for url in cpi_urls:
    filename = url.split("/")[-1]
    parsed_filename = parse_file_name(filename)
    download_files(url, path=f"{SAVED_PATH}{parsed_filename}.pdf")
