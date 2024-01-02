#!/usr/bin/env python
# coding: utf-8
import os
import sys
sys.path.insert(0, "/Users/czhang/Desktop/pacific-observatory/")
import pandas as pd
import glob
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


# 12 Yrs Data from 2010 to 2021
i = 0
while i < 12:
    chrome_options = webdriver.ChromeOptions()

    # Specify the downloading path
    prefs = {'download.default_directory': os.getcwd() + '/data/tonga'}
    chrome_options.add_experimental_option('prefs', prefs)
    driver = webdriver.Chrome(os.getcwd() + "/chromedriver", chrome_options=chrome_options)

    # Get the main page containing migration statistics
    driver.get("https://tongastats.gov.to/statistics/social-statistics/migration/#50-50-wpfd-top")

    # Each Year's folder button
    links =  WebDriverWait(driver, 5).until(
            EC.presence_of_all_elements_located((By.XPATH, "//a[@class='wpfdcategory catlink']")))

    # Click the button
    links[i].click()

    # Explicit Wait for elements loading
    time.sleep(5)

    # Check whether sub-folder exists (For 2016 and 2017)
    child_button = driver.find_elements(By.XPATH, "//a[@class='wpfdcategory catlink']")
    if len(child_button) > 1:
        child_button[-1].click()

    # Extract and click all the downloading buttons
    download_buttons = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.XPATH, "//a[@class='downloadlink wpfd_downloadlink']")))

    for button in download_buttons:
        button.click()

    # Explicit Wait for the downloading to be finished
    time.sleep(5)
    driver.close()
    i += 1