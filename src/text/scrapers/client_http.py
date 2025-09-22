"""
Asynchronous HTTP client for high-performance web scraping.

This module provides an AsyncHttpClient that uses httpx and asyncio
for concurrent HTTP requests, replacing the synchronous RequestsScraper.
"""

import asyncio
import logging
import time
from typing import List, Dict, Optional, Union, Any
import httpx
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from lxml import etree

# Disable httpx INFO logging to reduce noise
logging.getLogger("httpx").setLevel(logging.WARNING)

from .models import ScrapingResult, ThumbnailRecord, ArticleRecord

logger = logging.getLogger(__name__)


class AsyncHttpClient:
    """
    Asynchronous HTTP client for high-concurrency static scraping.
    
    This client uses httpx with asyncio for efficient concurrent requests
    and supports both BeautifulSoup and XPath parsing.
    """
    
    def __init__(
        self,
        parser: str = "html.parser",
        domain: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None,
        cookies: Optional[Dict[str, str]] = None,
        timeout: float = 60.0,
        max_concurrent: int = 10,
        rate_limit: float = 0.1  # Minimum delay between requests
    ):
        """
        Initialize the AsyncHttpClient.
        
        Args:
            parser: Parser type - "html.parser" or "xpath"
            domain: Domain for cookie management
            headers: Custom HTTP headers
            cookies: Custom cookies
            timeout: Request timeout in seconds
            max_concurrent: Maximum concurrent requests
            rate_limit: Minimum delay between requests (politeness)
        """
        if parser not in ["html.parser", "xpath"]:
            raise ValueError("Invalid parser. Use 'html.parser' or 'xpath'.")
        
        self.parser = parser
        self.domain = domain
        self.timeout = timeout
        self.max_concurrent = max_concurrent
        self.rate_limit = rate_limit
        
        # Default headers
        self.headers = headers or {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36",
        }
        
        # Cookie management
        self.cookies = cookies or {}
        if domain:
            self.refresh_cookies()
        
        # Semaphore for rate limiting
        self._semaphore = asyncio.Semaphore(max_concurrent)
        self._last_request_time = 0
    
    def refresh_cookies(self):
        """Fetch updated cookies for the domain."""
        if self.domain:
            try:
                new_cookies = configure_cookies(self.domain)
                self.cookies.update(new_cookies)
                logger.info(f"Refreshed cookies for domain: {self.domain}")
            except Exception as e:
                logger.warning(f"Failed to refresh cookies for {self.domain}: {e}")
    
    async def _rate_limit_delay(self):
        """Implement rate limiting between requests."""
        if self.rate_limit > 0:
            current_time = time.time()
            time_since_last = current_time - self._last_request_time
            if time_since_last < self.rate_limit:
                await asyncio.sleep(self.rate_limit - time_since_last)
            self._last_request_time = time.time()
    
    async def request_url(
        self,
        client: httpx.AsyncClient,
        url: str,
        retries: int = 3
    ) -> Optional[bytes]:
        """
        Send an async HTTP GET request to the specified URL.
        
        Args:
            client: httpx AsyncClient instance
            url: URL to request
            retries: Number of retry attempts
            
        Returns:
            Response content as bytes, or None if failed
        """
        async with self._semaphore:
            await self._rate_limit_delay()
            
            for attempt in range(retries + 1):
                try:
                    response = await client.get(
                        url,
                        headers=self.headers,
                        cookies=self.cookies,
                        timeout=self.timeout
                    )
                    response.raise_for_status()
                    return response.content
                    
                except httpx.HTTPStatusError as e:
                    if e.response.status_code == 404:
                        return None
                    if attempt == retries:  # Only log on final attempt
                        logger.warning(f"HTTP {e.response.status_code} for {url}")
                    
                except httpx.RequestError as e:
                    if attempt == retries:  # Only log on final attempt
                        logger.warning(f"Request error for {url}: {e}")
                    
                except Exception as e:
                    logger.error(f"Unexpected error for {url}: {e}")
                
                # Retry logic
                if attempt < retries:
                    wait_time = 2 ** attempt  # Exponential backoff
                    logger.info(f"Retrying {url} in {wait_time}s (attempt {attempt + 1}/{retries})")
                    await asyncio.sleep(wait_time)
                    
                    # Refresh cookies on retry
                    if self.domain and attempt == 0:
                        self.refresh_cookies()
            
            logger.error(f"Failed to retrieve {url} after {retries + 1} attempts")
            return None
    
    def parse_content(self, content: bytes) -> Union[BeautifulSoup, etree._Element]:
        """
        Parse HTTP response content using the specified parser.
        
        Args:
            content: Raw HTML content as bytes
            
        Returns:
            Parsed content object (BeautifulSoup or lxml etree)
        """
        if self.parser == "xpath":
            return etree.HTML(content.decode('utf-8', errors='ignore'))
        else:
            return BeautifulSoup(content, "html.parser")
    
    def extract_items(
        self,
        parsed_content: Union[BeautifulSoup, etree._Element],
        expression: str
    ) -> List[Any]:
        """
        Extract items from parsed content using the specified expression.
        
        Args:
            parsed_content: Parsed HTML content
            expression: CSS selector or XPath expression
            
        Returns:
            List of extracted elements
        """
        if self.parser == "xpath":
            return parsed_content.xpath(expression)
        else:
            # For BeautifulSoup, assume CSS selector
            if expression.startswith('.'):
                # Class selector
                class_name = expression[1:]  # Remove the dot
                return parsed_content.find_all(class_=class_name)
            else:
                # Tag selector or other CSS selector
                return parsed_content.select(expression)
    
    async def scrape_url(
        self,
        client: httpx.AsyncClient,
        url: str,
        expression: Union[str, List[str]]
    ) -> ScrapingResult:
        """
        Scrape a single URL with the given expression(s).
        
        Args:
            client: httpx AsyncClient instance
            url: URL to scrape
            expression: CSS selector/XPath expression or list of expressions
            
        Returns:
            ScrapingResult with extracted data or error information
        """
        try:
            content = await self.request_url(client, url)
            if content is None:
                return ScrapingResult(
                    success=False,
                    error="Failed to retrieve content",
                    url=url
                )
            
            parsed_content = self.parse_content(content)
            
            if isinstance(expression, str):
                items = self.extract_items(parsed_content, expression)
            elif isinstance(expression, list):
                items = [self.extract_items(parsed_content, expr) for expr in expression]
            else:
                raise ValueError("Expression must be string or list of strings")
            
            return ScrapingResult(
                success=True,
                data=items,
                url=url
            )
            
        except Exception as e:
            logger.error(f"Failed to scrape URL '{url}': {e}")
            return ScrapingResult(
                success=False,
                error=str(e),
                url=url
            )
    
    async def scrape_urls(
        self,
        urls: List[str],
        expression: Union[str, List[str]]
    ) -> List[ScrapingResult]:
        """
        Scrape multiple URLs concurrently.
        
        Args:
            urls: List of URLs to scrape
            expression: CSS selector/XPath expression or list of expressions
            
        Returns:
            List of ScrapingResult objects
        """
        if not isinstance(urls, list):
            raise TypeError("The 'urls' argument must be a list of URLs.")
        
        async with httpx.AsyncClient() as client:
            tasks = [
                self.scrape_url(client, url, expression)
                for url in urls
            ]
            
            # Use asyncio.gather for concurrent processing
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Handle any exceptions that occurred
            processed_results = []
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    processed_results.append(ScrapingResult(
                        success=False,
                        error=str(result),
                        url=urls[i]
                    ))
                else:
                    processed_results.append(result)
            
            return processed_results
    
    async def check_urls_batch(
        self,
        urls: List[str]
    ) -> Dict[str, bool]:
        """
        Check if a batch of URLs are accessible (for pagination detection).
        
        Args:
            urls: List of URLs to check
            
        Returns:
            Dictionary mapping URLs to their accessibility status
        """
        async with httpx.AsyncClient() as client:
            tasks = []
            for url in urls:
                tasks.append(self._check_single_url(client, url))
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            url_status = {}
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    url_status[urls[i]] = False
                else:
                    url_status[urls[i]] = result
            
            return url_status
    
    async def _check_single_url(self, client: httpx.AsyncClient, url: str) -> bool:
        """Check if a single URL is accessible."""
        try:
            async with self._semaphore:
                await self._rate_limit_delay()
                response = await client.head(
                    url,
                    headers=self.headers,
                    cookies=self.cookies,
                    timeout=self.timeout
                )
                return response.status_code == 200
        except Exception:
            return False
