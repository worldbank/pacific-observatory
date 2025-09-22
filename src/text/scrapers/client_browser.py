"""
Browser-based client for dynamic web scraping.

This module provides a BrowserClient that uses Selenium WebDriver
for scraping JavaScript-rendered content and handling dynamic sites.
"""

import time
from typing import List, Optional, Dict, Any, Union
from selenium import webdriver
from selenium.webdriver import ChromeService, ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.webelement import WebElement
from selenium.common.exceptions import (
    TimeoutException, 
    NoSuchElementException, 
    WebDriverException
)
import logging
from .models import ScrapingResult

logger = logging.getLogger(__name__)


class BrowserClient:
    """
    Browser-based client for dynamic scraping using Selenium WebDriver.
    
    This client handles JavaScript-rendered content and sites that require
    browser interaction for proper content loading.
    """
    
    def __init__(
        self,
        driver_path: Optional[str] = None,
        download_path: Optional[str] = None,
        headless: bool = True,
        timeout: float = 20.0,
        page_load_timeout: float = 30.0,
        implicit_wait: float = 10.0
    ):
        """
        Initialize the BrowserClient.
        
        Args:
            driver_path: Path to ChromeDriver executable (None for auto-detection)
            download_path: Directory for file downloads
            headless: Run browser in headless mode
            timeout: Default timeout for element waits
            page_load_timeout: Timeout for page loads
            implicit_wait: Implicit wait time for elements
        """
        self.driver_path = driver_path
        self.download_path = download_path
        self.headless = headless
        self.timeout = timeout
        self.page_load_timeout = page_load_timeout
        self.implicit_wait = implicit_wait
        
        self.driver: Optional[webdriver.Chrome] = None
        self.failed_urls: List[tuple] = []
    
    def start_driver(self):
        """Initialize and start the Chrome WebDriver."""
        try:
            # Configure Chrome service
            if self.driver_path:
                service = ChromeService(executable_path=self.driver_path)
            else:
                service = ChromeService()  # Auto-detect ChromeDriver
            
            # Configure Chrome options
            options = ChromeOptions()
            
            if self.headless:
                options.add_argument('--headless')
            
            # Performance and security options
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-gpu')
            options.add_argument('--disable-web-security')
            options.add_argument('--disable-features=VizDisplayCompositor')
            
            # Anti-detection options
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            options.add_argument('--disable-blink-features=AutomationControlled')
            
            # Download configuration
            if self.download_path:
                prefs = {
                    "download.default_directory": self.download_path,
                    "download.prompt_for_download": False,
                    "download.directory_upgrade": True,
                    "safebrowsing.enabled": True
                }
                options.add_experimental_option("prefs", prefs)
            
            # Initialize driver
            self.driver = webdriver.Chrome(service=service, options=options)
            
            # Set timeouts
            self.driver.set_page_load_timeout(self.page_load_timeout)
            self.driver.implicitly_wait(self.implicit_wait)
            
            # Execute script to hide automation indicators
            self.driver.execute_script(
                "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
            )
            
            logger.info("Chrome WebDriver started successfully")
            
        except Exception as e:
            logger.error(f"Failed to start Chrome WebDriver: {e}")
            raise
    
    def close_driver(self):
        """Close the WebDriver and clean up resources."""
        if self.driver:
            try:
                self.driver.quit()
                logger.info("Chrome WebDriver closed successfully")
            except Exception as e:
                logger.warning(f"Error closing WebDriver: {e}")
            finally:
                self.driver = None
    
    def navigate_to_url(self, url: str, retries: int = 3) -> bool:
        """
        Navigate to a URL with retry logic.
        
        Args:
            url: URL to navigate to
            retries: Number of retry attempts
            
        Returns:
            True if navigation successful, False otherwise
        """
        if not self.driver:
            raise RuntimeError("WebDriver not started. Call start_driver() first.")
        
        for attempt in range(retries + 1):
            try:
                self.driver.get(url)
                
                # Wait for basic page load
                WebDriverWait(self.driver, self.timeout).until(
                    lambda driver: driver.execute_script("return document.readyState") == "complete"
                )
                
                logger.debug(f"Successfully navigated to: {url}")
                return True
                
            except TimeoutException:
                logger.warning(f"Timeout loading {url} (attempt {attempt + 1})")
            except WebDriverException as e:
                logger.warning(f"WebDriver error for {url}: {e} (attempt {attempt + 1})")
            except Exception as e:
                logger.error(f"Unexpected error navigating to {url}: {e}")
                break
            
            if attempt < retries:
                wait_time = 2 ** attempt
                logger.info(f"Retrying navigation to {url} in {wait_time}s")
                time.sleep(wait_time)
        
        logger.error(f"Failed to navigate to {url} after {retries + 1} attempts")
        return False
    
    def find_elements(
        self,
        selector: str,
        by: By = By.XPATH,
        timeout: Optional[float] = None
    ) -> List[WebElement]:
        """
        Find elements using the specified selector.
        
        Args:
            selector: Element selector (XPath, CSS, etc.)
            by: Selenium By locator type
            timeout: Custom timeout (uses default if None)
            
        Returns:
            List of WebElement objects
        """
        if not self.driver:
            raise RuntimeError("WebDriver not started. Call start_driver() first.")
        
        timeout = timeout or self.timeout
        
        try:
            # Wait for at least one element to be present
            WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((by, selector))
            )
            
            # Return all matching elements
            elements = self.driver.find_elements(by, selector)
            logger.debug(f"Found {len(elements)} elements with selector: {selector}")
            return elements
            
        except TimeoutException:
            logger.warning(f"No elements found with selector: {selector}")
            return []
        except Exception as e:
            logger.error(f"Error finding elements with selector '{selector}': {e}")
            return []
    
    def extract_element_data(
        self,
        element: WebElement,
        data_type: str = "text"
    ) -> Optional[str]:
        """
        Extract data from a WebElement.
        
        Args:
            element: WebElement to extract data from
            data_type: Type of data to extract ('text', 'href', 'src', etc.)
            
        Returns:
            Extracted data as string, or None if extraction fails
        """
        try:
            if data_type == "text":
                return element.text.strip()
            elif data_type in ["href", "src", "alt", "title"]:
                return element.get_attribute(data_type)
            else:
                # Custom attribute
                return element.get_attribute(data_type)
                
        except Exception as e:
            logger.warning(f"Failed to extract {data_type} from element: {e}")
            return None
    
    def scrape_page(
        self,
        url: str,
        selectors: Dict[str, str],
        by: By = By.XPATH
    ) -> ScrapingResult:
        """
        Scrape a page using multiple selectors.
        
        Args:
            url: URL to scrape
            selectors: Dictionary mapping field names to selectors
            by: Selenium By locator type
            
        Returns:
            ScrapingResult with extracted data or error information
        """
        try:
            # Navigate to the URL
            if not self.navigate_to_url(url):
                return ScrapingResult(
                    success=False,
                    error="Failed to navigate to URL",
                    url=url
                )
            
            # Extract data using selectors
            extracted_data = {}
            for field_name, selector in selectors.items():
                elements = self.find_elements(selector, by)
                
                if elements:
                    # Extract data based on field name conventions
                    if field_name in ["url", "href", "link"]:
                        extracted_data[field_name] = self.extract_element_data(elements[0], "href")
                    elif field_name in ["title", "text", "content"]:
                        extracted_data[field_name] = self.extract_element_data(elements[0], "text")
                    elif field_name == "date":
                        extracted_data[field_name] = self.extract_element_data(elements[0], "text")
                    elif field_name == "body":
                        # For body, concatenate text from all matching elements
                        body_parts = []
                        for elem in elements:
                            text = self.extract_element_data(elem, "text")
                            if text:
                                body_parts.append(text)
                        extracted_data[field_name] = "\n".join(body_parts)
                    elif field_name == "tags":
                        # For tags, extract text from all matching elements
                        tags = []
                        for elem in elements:
                            tag = self.extract_element_data(elem, "text")
                            if tag:
                                tags.append(tag)
                        extracted_data[field_name] = tags
                    else:
                        # Default to text extraction
                        extracted_data[field_name] = self.extract_element_data(elements[0], "text")
                else:
                    extracted_data[field_name] = None
            
            return ScrapingResult(
                success=True,
                data=extracted_data,
                url=url
            )
            
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Failed to scrape page '{url}': {error_msg}")
            self.failed_urls.append((url, error_msg))
            
            return ScrapingResult(
                success=False,
                error=error_msg,
                url=url
            )
    
    def scrape_multiple_pages(
        self,
        urls: List[str],
        selectors: Dict[str, str],
        by: By = By.XPATH
    ) -> List[ScrapingResult]:
        """
        Scrape multiple pages sequentially.
        
        Args:
            urls: List of URLs to scrape
            selectors: Dictionary mapping field names to selectors
            by: Selenium By locator type
            
        Returns:
            List of ScrapingResult objects
        """
        results = []
        
        for url in urls:
            result = self.scrape_page(url, selectors, by)
            results.append(result)
            
            # Small delay between requests for politeness
            time.sleep(1)
        
        return results
    
    def wait_for_element(
        self,
        selector: str,
        by: By = By.XPATH,
        timeout: Optional[float] = None,
        condition: str = "presence"
    ) -> Optional[WebElement]:
        """
        Wait for an element to meet a specific condition.
        
        Args:
            selector: Element selector
            by: Selenium By locator type
            timeout: Custom timeout
            condition: Wait condition ('presence', 'visible', 'clickable')
            
        Returns:
            WebElement if found, None otherwise
        """
        if not self.driver:
            raise RuntimeError("WebDriver not started. Call start_driver() first.")
        
        timeout = timeout or self.timeout
        
        try:
            wait = WebDriverWait(self.driver, timeout)
            
            if condition == "presence":
                element = wait.until(EC.presence_of_element_located((by, selector)))
            elif condition == "visible":
                element = wait.until(EC.visibility_of_element_located((by, selector)))
            elif condition == "clickable":
                element = wait.until(EC.element_to_be_clickable((by, selector)))
            else:
                raise ValueError(f"Unknown condition: {condition}")
            
            return element
            
        except TimeoutException:
            logger.warning(f"Element not found with condition '{condition}': {selector}")
            return None
        except Exception as e:
            logger.error(f"Error waiting for element '{selector}': {e}")
            return None
    
    def execute_script(self, script: str, *args) -> Any:
        """
        Execute JavaScript in the browser.
        
        Args:
            script: JavaScript code to execute
            *args: Arguments to pass to the script
            
        Returns:
            Result of script execution
        """
        if not self.driver:
            raise RuntimeError("WebDriver not started. Call start_driver() first.")
        
        try:
            return self.driver.execute_script(script, *args)
        except Exception as e:
            logger.error(f"Error executing script: {e}")
            return None
    
    def get_page_source(self) -> str:
        """Get the current page's HTML source."""
        if not self.driver:
            raise RuntimeError("WebDriver not started. Call start_driver() first.")
        
        return self.driver.page_source
    
    def __enter__(self):
        """Context manager entry."""
        self.start_driver()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close_driver()
