#!/usr/bin/env python
# coding: utf-8
import os
import pandas as pd
import glob
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import time
import random


# 12 Yrs
i = 0
while i < 12:
    chrome_options = webdriver.ChromeOptions()

    # Specify the downloading path
    prefs = {'download.default_directory': os.getcwd() + '/data/tonga'}
    chrome_options.add_experimental_option('prefs', prefs)
    driver = webdriver.Chrome(os.getcwd()+ "/chromedriver", chrome_options=chrome_options)

    # Get the main page containing migration statistics
    driver.get("https://tongastats.gov.to/statistics/social-statistics/migration/#50-50-wpfd-top")
    time.sleep(3)


    links = driver.find_elements(
        By.XPATH, "//a[@class='wpfdcategory catlink']")  # Each Year's folder button

    links[i].click()  # Click the button
    time.sleep(3) # Sleep to allow page loading

    download_buttons = driver.find_elements(
        By.XPATH, "//a[@class='downloadlink wpfd_downloadlink']")
    for button in download_buttons:
        button.click()

    time.sleep(3)

    driver.close()
    i += 1
