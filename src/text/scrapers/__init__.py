import time
import multiprocessing
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests
from bs4 import BeautifulSoup
from lxml import etree
from tqdm import tqdm
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver import ChromeService, ChromeOptions
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from .utils import configure_cookies
import pandas as pd
import os


class RequestsScraper(object):
    def __init__(self, parser="xpath",
                 domain=None,
                 headers=None, 
                 cookies=None,
                 cookies_path=None):
        """
        A class for web scraping using either HTML or XPath parsing.

        Args:
            parser (str, optional): The parser to use for parsing the web page. 
                Either "HTML" (default) or "XPATH". 
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
        if headers is None:
            self.headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36",
            }
        else:
            self.headers = headers
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        self.domain = domain
        self.cookies_path = cookies_path
        self.cookies = {}
        if domain:
            self.refresh_cookies()
        self.item_container = None


    def refresh_cookies(self):
        """
        Fetches updated cookies and updates the scraper's cookie jar.
        """
        new_cookies = configure_cookies(self.domain)
        self.cookies.update(new_cookies)

    def request_url(self, url, timeout=60, retries=3):
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
        """
        Scrape single url's content by a given expression.
        """
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
                            print(f'{url} generated an exception: {exc}')
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

    def __init__(self, driver_path, download_path):
        """
        Initialize the WebScraper object.

        Args:
            driver_path (str): The path to the ChromeDriver executable.
            url (str): The URL to be scraped.
        """
        self.driver_path = driver_path
        self.download_path = download_path
        self.failed_urls = []
        self.driver = None

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
        if self.download_path:
            prefs = {"download.default_directory": self.download_path}
            options.add_experimental_option("prefs", prefs)
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
        """
        Scrapes the specified URL with the given search query.

        Args:
            url (str): The URL of the web page to be scraped.
            search_query (str): The search query to find elements on the page.

        Returns:
            list or None: A list of WebElement objects if elements are found; None if an error occurs.
        """
        self.driver.get(url)
        try:
            elements = self.perform_search(search_query)
            return elements
        except Exception as e:
            self.failed_urls.append((url, str(e)))
            return None
    

class NewspaperScraper(RequestsScraper, SeleniumScraper):
    name: str
    domain: str
    region: str
    target_dir: str
    page_urls: list
    urls_df: pd.DataFrame
    previous_news_df: pd.DataFrame
    
    def __init__(self, name, domain, region, urls_df=None, *args, **kwargs):
        self.name = name
        self.domain = domain
        self.region = region
        self.urls_df = urls_df
        self.target_dir = os.environ["DATA_FOLDER_PATH"] + f"/text/{self.region}/{self.name}/"
        super().__init__(*args, **kwargs)

    def get_page_enum(self):
        pass

    def get_news_urls(self):
        pass

    def save_news_urls(self):
        """Save the scraped URLs to CSV file."""
        if self.urls_df is not None:
            urls_file = self.target_dir + "urls.csv"
            self.urls_df.to_csv(urls_file, encoding="utf-8", index=False)
            print(f"Saved URLs to {urls_file}")

    def get_new_news(self):
        """Get new news URLs to scrape."""
        if self.urls_df is None:
            raise ValueError("Must call get_news_urls() first")
        
        # Determine which URLs to scrape
        if len(self.previous_news_df) > 0:
            previous_urls = set(self.previous_news_df["url"])
            current_urls = set(self.urls_df["url"])
            urls_to_scrape = list(current_urls - previous_urls)
            print(f"Scraping {len(urls_to_scrape)} new articles")
        else:
            urls_to_scrape = self.urls_df["url"].tolist()
            print(f"Scraping all {len(urls_to_scrape)} articles")
        return urls_to_scrape

    def get_previous_news(self):
        """Load previously scraped news data."""
        news_file = self.target_dir + "news.csv"
        
        try:
            self.previous_news_df = pd.read_csv(news_file)
            if "Unnamed: 0" in self.previous_news_df.columns:
                self.previous_news_df = self.previous_news_df.drop("Unnamed: 0", axis=1)
            self.previous_news_df["date"] = pd.to_datetime(
                self.previous_news_df["date"], format="mixed"
            )
            print(f"Loaded {len(self.previous_news_df)} existing articles")
        except FileNotFoundError:
            print("No previous news file found, will create new one")
            self.previous_news_df = pd.DataFrame(columns=["url", "title", "date", "news", "tag"])
        
        return self.previous_news_df

    def scrape_news(self):
        pass

    def save_scraped_news(self, news_df):
        """Save the scraped news data, combining with previous data if needed."""
        news_file = self.target_dir + "news.csv"
        
        if self.previous_news_df is not None and len(self.previous_news_df) > 0:
            # Combine with previous data
            current_news_df = pd.concat([news_df, self.previous_news_df], axis=0)
            current_news_df = (
                current_news_df.sort_values(by="date", ascending=False)
                .reset_index(drop=True)
            )
            current_news_df.to_csv(news_file, encoding="utf-8", index=False)
            print(f"Saved {len(current_news_df)} total articles to {news_file}")
        else:
            # Save only new data
            news_df.to_csv(news_file, encoding="utf-8", index=False)
            print(f"Saved {len(news_df)} articles to {news_file}")


class CountryScraper:
    def __init__(self, newscraperscrapers):
        self.newscraperscrapers = newscraperscrapers

    def get_page_enum(self):
        for newscraperscraper in self.newscraperscrapers:
            newscraperscraper.get_page_enum()

    def get_news_urls(self):
        for newscraperscraper in self.newscraperscrapers:
            newscraperscraper.get_news_urls()

    def save_news_urls(self):
        for newscraperscraper in self.newscraperscrapers:
            newscraperscraper.save_news_urls()

    def get_previous_news(self):
        for newscraperscraper in self.newscraperscrapers:
            newscraperscraper.get_previous_news()

    def scrape_news(self):
        for newscraperscraper in self.newscraperscrapers:
            newscraperscraper.scrape_news()

    def save_scraped_news(self):
        for newscraperscraper in self.newscraperscrapers:
            newscraperscraper.save_scraped_news()
    
    