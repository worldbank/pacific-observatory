import os
import numpy as np
import pandas as pd
import requests
from bs4 import BeautifulSoup
import urllib
from lxml import etree
from tqdm import tqdm
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
import multiprocessing
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver import ChromeService, ChromeOptions
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from .utils import download_files, configure_cookies, configure_headers


class WebScraper(object):
    def __init__(self, parser="xpath",
                 domain=None,
                 headers=None, 
                 cookies=None,
                 cookies_path=None):
        """
        A class for web scraping using either HTML or XPath parsing.

        Args:
            parser (str, optional): The parser to use for parsing the web page. Either "HTML" (default) or "XPATH".
            headers (dict, optional): Custom headers to use for HTTP requests.

        Raises:
            ValueError: If an invalid parser is provided.

        Attributes:
            parser (str): The selected parser ("HTML" or "XPATH").
            headers (dict): HTTP headers to use for requests.
        """
        if parser not in ["html.parser", "xpath"]:
            raise ValueError("Invalid parser. Use 'html.parser' or 'xpath'.")

        self.parser = parser
        if headers == None:
            self.headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36",
            }
        else:
            self.headers = headers
        self.session = requests.Session()
        self.session.headers.update(headers)
        self.domain = domain
        self.cookies_path = cookies_path
        self.cookies = {}
        if domain:
            self.refresh_cookies()


    def refresh_cookies(self):
        """
        Fetches updated cookies and updates the scraper's cookie jar.
        """
        new_cookies = configure_cookies(self.domain, self.cookies_path)
        self.cookies.update(new_cookies)

    def request_url(self, url, timeout=30, retries=3):
        """
        Sends an HTTP GET request to the specified URL.

        Args:
            url (str): The URL to send the request to.
            timeout (int): The timeout value for the request in seconds (default is 5).

        Returns:
            bytes: The content of the HTTP response.
        """ 
        try:
            response = self.session.get(
                url, headers=self.headers, timeout=timeout, cookies=self.cookies)
            response.raise_for_status()
            return response.content
        except requests.exceptions.RequestException as e:
            time.sleep(5)
            if retries > 0:
                print(f"Failed to retrieve the page, attempting to refresh cookies and retry: {e}")
                self.refresh_cookies()  # Refresh cookies if request fails
                return self.request_url(url, timeout, retries - 1)  # Decrement retries and retry the request
            else:
                print(f"Failed to retrieve the page after retries: {e}")
                return None

    def parse_content(self, content):
        """
         Parses the HTTP response content using the specified parser.

        Args:
            content (bytes): The content to be parsed.

        Returns:
            object: The parsed content object (either lxml.etree or BeautifulSoup).
        """

        return etree.HTML(str(content)) if self.parser == "xpath" else BeautifulSoup(
            content, "html.parser")

    def extract_items(self, parsed_content,
                      expression: str):
        """

        Extracts items from the parsed content based on the specified expression.

        Args:
            parsed_content (object): The parsed content object.
            expression (str): The expression used for extraction.

        Returns:
            list: A list of extracted items.
        """

        if self.parser == "xpath":
            self.item_container = parsed_content.xpath(expression)
        else:
            self.item_container = parsed_content.find_all(
                class_=expression)
        return self.item_container

    def scrape_url(self, url, expression):

        try:
            content = self.request_url(url)
            parsed_content = self.parse_content(content)
            if isinstance(expression, str):
                items = self.extract_items(parsed_content, expression)
            elif isinstance(expression, list):
                items = [self.extract_items(parsed_content, expr)
                         for expr in expression]
        except Exception as e:
            items = []
            print(f"Failed to scrape URL '{url}': {e}")
        return items

    def scrape_urls(self, urls, expression, speed_up=False):
        if not isinstance(urls, list):
            raise TypeError("The 'urls' argument must be a list of URLs.")

        # if isinstance(expression, str):
        #     expression = [expression] * len(urls)

        # if not isinstance(expression, list) or len(expression) != len(urls):
        #     raise ValueError(
        #         "The 'expression' argument must be a string or a list of the same length as 'urls'."
        #     )

        # if isinstance(expression, list):
        #     expression = [expression * len(urls)]

        scraped_data = []
        if speed_up:
            with tqdm(total=len(urls)) as pbar:
                max_workers = multiprocessing.cpu_count() + 4 if not self.domain else multiprocessing.cpu_count() 
                with ThreadPoolExecutor(max_workers=max_workers) as executor:
                    future_to_url = {executor.submit(self.scrape_url, url, expression): (
                        url) for url in urls}
                    for future in as_completed(future_to_url):
                        url = future_to_url[future]
                        try:
                            data = future.result()
                        except Exception as exc:
                            print('%r generated an exception: %s' % (url, exc))
                        else:
                            scraped_data.append([url, data])
                            pbar.update(1)
        else:
            with tqdm(total=len(urls)) as pbar:
                for url in urls:
                    data = self.scrape_url(url, expression)
                    scraped_data.append(data)
                    pbar.update(1)

        return scraped_data


class SeleniumScraper:
    """
    A class for web scraping using Selenium with ChromeDriver.

    Attributes:
        driver_path (str): The path to the ChromeDriver executable.
        url (str): The URL to be scraped.
        driver: Instance of the ChromeDriver.

    Methods:
        start_driver(): Start the ChromeDriver.
        close_driver(): Close the ChromeDriver.
        perform_search(search_query): Perform a search on the web page.

    Usage:
        scraper = WebScraper(driver_path='/path/to/chromedriver')
        scraper.start_driver()
        scraper.perform_search('web scraping')
        scraper.close_driver()
    """

    def __init__(self, driver_path):
        """
        Initialize the WebScraper object.

        Args:
            driver_path (str): The path to the ChromeDriver executable.
            url (str): The URL to be scraped.
        """
        self.driver_path = driver_path
        self.failed_urls = []

    def start_driver(self):
        """
        Start the ChromeDriver.
        """
        service = ChromeService(executable_path=self.driver_path)
        options = ChromeOptions()
        options.headless = True
        options.add_experimental_option(
            "excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        self.driver = webdriver.Chrome(service=service, options=options)

    def close_driver(self):
        """
        Close the ChromeDriver.
        """
        if self.driver:
            self.driver.quit()

    def perform_search(self, search_query):
        """
        Perform a search on the web page.

        Args:
            search_query (str): The search query to be entered.
        """
        elements = WebDriverWait(self.driver, 20).until(
            EC.presence_of_all_elements_located((By.XPATH, search_query)))
        return elements
    
    def scrape_page(self, url, search_query):
        self.driver.get(url)
        try:
            elements = self.perform_search(search_query)
            return elements
        except:
            self.failed_urls.append(url)
            pass 
