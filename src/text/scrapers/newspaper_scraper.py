"""
Generic newspaper scraper driven by configuration.

This module provides a NewspaperScraper class that can scrape any newspaper
based on a configuration dictionary, using the appropriate client and strategy.
"""

import asyncio
import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Any, Union
from urllib.parse import urljoin, urlparse
import httpx
from .client_http import AsyncHttpClient
from .client_browser import BrowserClient
from .listing_strategies import create_listing_strategy
from .models import (
    ThumbnailRecord, 
    ArticleRecord, 
    ScrapingResult, 
    NewspaperConfig
)
from .pipelines.cleaning import apply_cleaning
from .pipelines.storage import JsonlStorage

logger = logging.getLogger(__name__)


class NewspaperScraper:
    """
    Generic newspaper scraper driven by configuration.
    
    This class can scrape any newspaper based on a configuration
    dictionary that specifies selectors, listing strategy, and
    other site-specific parameters.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the newspaper scraper with configuration.
        
        Args:
            config: Configuration dictionary (validated against NewspaperConfig)
        """
        # Validate configuration
        self.config = NewspaperConfig(**config)
        
        # Basic properties
        self.name = self.config.name
        self.country = self.config.country
        self.base_url = str(self.config.base_url)
        
        # Initialize client based on configuration
        self.client_type = self.config.client
        self._http_client: Optional[AsyncHttpClient] = None
        self._browser_client: Optional[BrowserClient] = None
        
        # Initialize listing strategy
        self.listing_strategy = create_listing_strategy(self.config.listing)
        
        # Selectors for data extraction
        self.selectors = self.config.selectors
        
        # Data storage
        self.scraped_thumbnails: List[ThumbnailRecord] = []
        self.scraped_articles: List[ArticleRecord] = []
        self.failed_urls: List[Dict[str, Any]] = []
        self.failed_news: List[Dict[str, Any]] = []
        self._saved_files = {}  # Track files saved by this scraper
        
        # Initialize storage system
        self._storage = JsonlStorage()
    
    def _get_http_client(self) -> AsyncHttpClient:
        """Get or create HTTP client."""
        if self._http_client is None:
            # Extract domain for cookie management
            domain = urlparse(self.base_url).netloc
            
            # Configure client based on auth settings
            auth_config = self.config.auth or {}
            
            # Get client configuration parameters from config
            concurrency = self.config.concurrency or 10
            rate_limit = self.config.rate_limit or 0.1
            retries = self.config.retries or 3
            retry_seconds = self.config.retry_seconds or 2.0
            
            # Get headers from config - this was the critical missing piece!
            headers = self.config.headers or {}
            
            logger.info(f"Creating HTTP client for {self.name}")
            logger.info(f"Domain: {domain}")
            logger.info(f"Loading headers from config")
            logger.info(f"Concurrency: {concurrency}, Rate limit: {rate_limit}")
            logger.info(f"Retries: {retries}, Retry delay: {retry_seconds}s")
            
            self._http_client = AsyncHttpClient(
                parser="html.parser",  # Default to BeautifulSoup
                domain=domain if auth_config else None,
                headers=headers,  # Pass config headers to client
                timeout=60.0,
                max_concurrent=concurrency,
                rate_limit=rate_limit,
                retries=retries,
                retry_seconds=retry_seconds
            )
            
        return self._http_client
    
    def _get_browser_client(self) -> BrowserClient:
        """Get or create browser client."""
        if self._browser_client is None:
            self._browser_client = BrowserClient(
                headless=True,
                timeout=20.0,
                page_load_timeout=30.0
            )
        
        return self._browser_client
    
    async def discover_and_scrape_thumbnails(self) -> List[ThumbnailRecord]:
        """
        Discover listing pages and scrape thumbnails, with smart caching and retry logic.
        
        First checks if today's thumbnails already exist. If yes, loads them.
        If no, performs discovery and scraping with retry logic for failed pages.
        If no thumbnails are found, retries up to 25 times with 2-second delays.
        
        Returns:
            List of ThumbnailRecord objects
        """
        # Try to load existing thumbnails from today's file
        existing_thumbnails = self._storage.load_thumbnails_from_urls_file(self.country, self.name)
        if existing_thumbnails:
            logger.info("Using existing thumbnails from today's file - skipping discovery")
            return existing_thumbnails
        
        # No existing file, perform discovery and scraping
        logger.info("No existing thumbnails found - performing discovery and scraping")
        
        if self.client_type == "http":
            client = self._get_http_client()
        else:
            raise NotImplementedError("Browser client not yet supported for combined discovery/scraping")
        
        thumbnails = []
        thumbnail_selector = self.selectors["thumbnail"]
        
        # Use the combined discover_and_scrape method from the pagination strategy
        if hasattr(self.listing_strategy, 'discover_and_scrape'):
            async for result_batch in self.listing_strategy.discover_and_scrape(client, self.base_url, thumbnail_selector):
                for result in result_batch:
                    if not result.success:
                        self.failed_urls.append({
                            "url": str(result.url),
                            "status_code": result.status_code,
                            "error": result.error,
                            "stage": "thumbnail_listing"
                        })
                        continue
                    
                    # Parse the scraped content
                    thumbnail_elements = result.data
                    if not thumbnail_elements:
                        # No thumbnails found - implement retry logic
                        logger.warning(f"No thumbnails found on {result.url} - starting retry sequence")
                        
                        # Retry up to 25 times with 2-second delays
                        retry_count = 0
                        max_retries = 25
                        retry_delay = 2.0
                        
                        while retry_count < max_retries:
                            retry_count += 1
                            logger.debug(f"Retry {retry_count}/{max_retries} for {result.url}")
                            
                            # Wait before retry
                            await asyncio.sleep(retry_delay)
                            
                            # Retry the request
                            try:
                                retry_result = await client.scrape_url(client._http_client, str(result.url), thumbnail_selector)
                                
                                if retry_result.success and retry_result.data:
                                    logger.info(f"Thumbnails found on retry {retry_count} for {result.url}")
                                    thumbnail_elements = retry_result.data
                                    break
                                    
                            except Exception as e:
                                logger.debug(f"Retry {retry_count} failed for {result.url}: {e}")
                        
                        # If still no thumbnails after all retries, mark as failed
                        if not thumbnail_elements:
                            logger.warning(f"No thumbnails found after {max_retries} retries for {result.url}")
                            self.failed_urls.append({
                                "url": str(result.url),
                                "status_code": getattr(result, 'status_code', None),
                                "error": f"No thumbnails found after {max_retries} retries",
                                "stage": "thumbnail_listing_no_content"
                            })
                            continue
                    
                    # Extract data from each thumbnail element
                    for thumb_elem in thumbnail_elements:
                        thumb_data = self._extract_thumbnail_data_from_element(thumb_elem, str(result.url))
                        if thumb_data:
                            try:
                                thumbnail = ThumbnailRecord(**thumb_data)
                                thumbnails.append(thumbnail)
                            except Exception as e:
                                logger.error(f"Failed to create ThumbnailRecord: {e}")
                                logger.error(f"Data: {thumb_data}")
                
                logger.info(f"Processed batch: {len(result_batch)} pages, {len(thumbnails)} total thumbnails")
        else:
            # Fallback to old method for strategies that don't support combined approach
            listing_urls = await self.discover_listing_urls()
            thumbnails = await self.scrape_thumbnails_with_retry(listing_urls)
        
        logger.info(f"Total thumbnails discovered and scraped: {len(thumbnails)}")
        
        # Save thumbnails to JSONL file
        saved_path = self._storage.save_thumbnails_as_urls(thumbnails, self.country, self.name)
        if saved_path:
            self._saved_files['urls'] = saved_path
        
        return thumbnails

    async def discover_listing_urls(self) -> List[str]:
        """
        Discover listing page URLs using the configured strategy.
        
        Returns:
            List of listing page URLs to scrape for thumbnails
        """
        if self.client_type == "http":
            client = self._get_http_client()
        else:
            raise NotImplementedError("Browser client not yet supported for listing discovery")
        
        all_urls = []
        
        async for url_batch in self.listing_strategy.discover_urls(client, self.base_url):
            all_urls.extend(url_batch)
            logger.info(f"Discovered {len(url_batch)} listing URLs (total: {len(all_urls)})")
        
        logger.info(f"Total listing URLs discovered: {len(all_urls)}")
        return all_urls
    
    def _extract_thumbnail_data_from_element(self, thumbnail_element, page_url: str) -> Optional[Dict[str, Any]]:
        """
        Extract thumbnail data directly from a thumbnail element.
        
        Args:
            thumbnail_element: Individual thumbnail element (BeautifulSoup element)
            page_url: URL of the page this element came from
            
        Returns:
            Dictionary with extracted data or None if extraction failed
        """
        try:
            data = {}
            
            # Extract title
            title_selector = self.selectors.get("title")
            if title_selector:
                if title_selector.endswith("::text"):
                    # CSS selector with text extraction
                    selector = title_selector.replace("::text", "")
                    title_elem = thumbnail_element.select_one(selector)
                    data["title"] = title_elem.get_text(strip=True) if title_elem else None
                elif title_selector.endswith("::attr(href)") or title_selector.endswith("::attr(src)"):
                    # CSS selector with attribute extraction
                    attr_name = title_selector.split("::attr(")[1].rstrip(")")
                    selector = title_selector.split("::attr(")[0]
                    title_elem = thumbnail_element.select_one(selector)
                    data["title"] = title_elem.get(attr_name) if title_elem else None
                else:
                    # Regular CSS selector
                    title_elem = thumbnail_element.select_one(title_selector)
                    data["title"] = title_elem.get_text(strip=True) if title_elem else None
            
            # Extract URL
            url_selector = self.selectors.get("url")
            if url_selector:
                if url_selector.endswith("::attr(href)"):
                    # CSS selector with href extraction
                    selector = url_selector.replace("::attr(href)", "")
                    url_elem = thumbnail_element.select_one(selector)
                    if url_elem:
                        href = url_elem.get("href")
                        # Make URL absolute
                        data["url"] = urljoin(self.base_url, href) if href else None
                else:
                    # Regular CSS selector - assume it's a link
                    url_elem = thumbnail_element.select_one(url_selector)
                    if url_elem:
                        href = url_elem.get("href")
                        data["url"] = urljoin(self.base_url, href) if href else None
            
            # Extract date
            date_selector = self.selectors.get("date")
            if date_selector:
                if date_selector.endswith("::text"):
                    selector = date_selector.replace("::text", "")
                    date_elem = thumbnail_element.select_one(selector)
                    data["date"] = date_elem.get_text(strip=True) if date_elem else None
                else:
                    date_elem = thumbnail_element.select_one(date_selector)
                    data["date"] = date_elem.get_text(strip=True) if date_elem else None
            
            # Validate that we have the essential data
            if not data.get("title") or not data.get("url"):
                logger.warning("Thumbnail missing essential data (title or URL)")
                return None
            
            # Apply cleaning functions if configured
            cleaning_config = self.config.cleaning
            if cleaning_config:
                data = apply_cleaning(data, cleaning_config, self.base_url)
            
            return data
            
        except Exception as e:
            logger.error(f"Error extracting thumbnail data: {e}")
            return None

    async def scrape_thumbnails_with_retry(self, listing_urls: List[str]) -> List[ThumbnailRecord]:
        """
        Scrape thumbnail data from listing pages with retry logic.
        
        Args:
            listing_urls: List of listing page URLs
            
        Returns:
            List of ThumbnailRecord objects
        """
        thumbnails = []
        
        if self.client_type == "http":
            client = self._get_http_client()
            
            # Scrape all listing pages
            thumbnail_selector = self.selectors["thumbnail"]
            results = await client.scrape_urls(listing_urls, thumbnail_selector)
            
            for result in results:
                if not result.success:
                    self.failed_urls.append({
                        "url": str(result.url),
                        "status_code": result.status_code,
                        "error": result.error,
                        "stage": "thumbnail_listing"
                    })
                    continue
                
                # Parse the scraped content
                thumbnail_elements = result.data
                if not thumbnail_elements:
                    # No thumbnails found - implement retry logic
                    logger.warning(f"No thumbnails found on {result.url} - starting retry sequence")
                    
                    # Retry up to 25 times with 2-second delays
                    retry_count = 0
                    max_retries = 25
                    retry_delay = 2.0
                    
                    while retry_count < max_retries:
                        retry_count += 1
                        logger.debug(f"Retry {retry_count}/{max_retries} for {result.url}")
                        
                        # Wait before retry
                        await asyncio.sleep(retry_delay)
                        
                        # Retry the request
                        try:
                            retry_result = await client.scrape_url(client._http_client, str(result.url), thumbnail_selector)
                            
                            if retry_result.success and retry_result.data:
                                logger.info(f"Thumbnails found on retry {retry_count} for {result.url}")
                                thumbnail_elements = retry_result.data
                                break
                                
                        except Exception as e:
                            logger.debug(f"Retry {retry_count} failed for {result.url}: {e}")
                    
                    # If still no thumbnails after all retries, mark as failed
                    if not thumbnail_elements:
                        logger.warning(f"No thumbnails found after {max_retries} retries for {result.url}")
                        self.failed_urls.append({
                            "url": str(result.url),
                            "status_code": getattr(result, 'status_code', None),
                            "error": f"No thumbnails found after {max_retries} retries",
                            "stage": "thumbnail_listing_no_content"
                        })
                        continue
                
                # Extract data from each thumbnail element
                for thumb_elem in thumbnail_elements:
                    thumb_data = self._extract_thumbnail_data_from_element(thumb_elem, str(result.url))
                    if thumb_data:
                        try:
                            thumbnail = ThumbnailRecord(**thumb_data)
                            thumbnails.append(thumbnail)
                        except Exception as e:
                            logger.error(f"Failed to create ThumbnailRecord: {e}")
                            logger.error(f"Data: {thumb_data}")
        
        else:
            # Browser client implementation with retry logic
            browser_client = self._get_browser_client()
            
            try:
                browser_client.start_driver()
                
                for url in listing_urls:
                    try:
                        if not browser_client.navigate_to_url(url):
                            self.failed_urls.append({
                                "url": url,
                                "error": "Failed to navigate",
                                "stage": "thumbnail_listing"
                            })
                            continue
                        
                        # Find thumbnail elements
                        thumbnail_selector = self.selectors["thumbnail"]
                        thumbnail_elements = browser_client.find_elements(thumbnail_selector)
                        
                        if not thumbnail_elements:
                            # No thumbnails found - implement retry logic
                            logger.warning(f"No thumbnails found on {url} - starting retry sequence")
                            
                            # Retry up to 25 times with 2-second delays
                            retry_count = 0
                            max_retries = 25
                            retry_delay = 2.0
                            
                            while retry_count < max_retries:
                                retry_count += 1
                                logger.debug(f"Retry {retry_count}/{max_retries} for {url}")
                                
                                # Wait before retry
                                await asyncio.sleep(retry_delay)
                                
                                # Retry navigation and element finding
                                try:
                                    if browser_client.navigate_to_url(url):
                                        thumbnail_elements = browser_client.find_elements(thumbnail_selector)
                                        if thumbnail_elements:
                                            logger.info(f"Thumbnails found on retry {retry_count} for {url}")
                                            break
                                except Exception as e:
                                    logger.debug(f"Retry {retry_count} failed for {url}: {e}")
                            
                            # If still no thumbnails after all retries, mark as failed
                            if not thumbnail_elements:
                                logger.warning(f"No thumbnails found after {max_retries} retries for {url}")
                                self.failed_urls.append({
                                    "url": url,
                                    "error": f"No thumbnails found after {max_retries} retries",
                                    "stage": "thumbnail_listing_no_content"
                                })
                                continue
                        
                        # Extract data from each thumbnail
                        for thumb_elem in thumbnail_elements:
                            try:
                                # Extract basic data using browser client methods
                                title = browser_client.extract_element_data(thumb_elem, "text")
                                href = browser_client.extract_element_data(thumb_elem, "href")
                                
                                if title and href:
                                    thumb_data = {
                                        "title": title,
                                        "url": urljoin(self.base_url, href),
                                        "date": "Unknown"  # Would need more sophisticated extraction
                                    }
                                    
                                    thumbnail = ThumbnailRecord(**thumb_data)
                                    thumbnails.append(thumbnail)
                                    
                            except Exception as e:
                                logger.error(f"Error processing thumbnail element: {e}")
                    
                    except Exception as e:
                        self.failed_urls.append({
                            "url": url,
                            "error": str(e),
                            "stage": "thumbnail_listing"
                        })
            
            finally:
                browser_client.close_driver()
        
        logger.info(f"Scraped {len(thumbnails)} thumbnails from {len(listing_urls)} listing pages")
        self.scraped_thumbnails = thumbnails
        return thumbnails

    async def scrape_thumbnails(self, listing_urls: List[str]) -> List[ThumbnailRecord]:
        """
        Scrape thumbnail data from listing pages (legacy method without retry).
        
        Args:
            listing_urls: List of listing page URLs
            
        Returns:
            List of ThumbnailRecord objects
        """
        # Delegate to the retry version for consistency
        return await self.scrape_thumbnails_with_retry(listing_urls)
    
    async def scrape_articles(self, thumbnails: List[ThumbnailRecord]) -> List[ArticleRecord]:
        """
        Scrape full article content from thumbnail URLs with progress tracking.
        
        Args:
            thumbnails: List of ThumbnailRecord objects
            
        Returns:
            List of ArticleRecord objects
        """
        articles = []
        article_urls = [str(thumb.url) for thumb in thumbnails]
        
        if self.client_type == "http":
            client = self._get_http_client()
            
            # Create selectors for article extraction
            article_selectors = {
                "title": self.selectors.get("title", "h1"),
                "body": self.selectors.get("article_body", "article"),
                "tags": self.selectors.get("tags", "")
            }
            
            # Import tqdm for progress tracking
            from tqdm.asyncio import tqdm
            
            # Scrape articles with tqdm progress bar
            logger.info(f"Scraping {len(article_urls)} articles...")
            
            # Process with tqdm progress bar
            async with httpx.AsyncClient() as http_client:
                for i, thumbnail in enumerate(tqdm(thumbnails, desc="Scraping articles")):
                    try:
                        # Scrape individual article
                        result = await client.scrape_url(http_client, str(thumbnail.url), list(article_selectors.values()))
                        
                        if not result.success:
                            self.failed_news.append({
                                "url": str(thumbnail.url),
                                "status_code": result.status_code,
                                "error": result.error,
                                "stage": "article_content"
                            })
                            continue
                        
                        # Extract article data (simplified - would need more sophisticated extraction)
                        article_data = {
                            "url": str(thumbnail.url),
                            "title": thumbnail.title,
                            "date": thumbnail.date,
                            "body": "Article content would be extracted here",  # Placeholder
                            "tags": [],
                            "source": self.name,
                            "country": self.country
                        }
                        
                        article = ArticleRecord(**article_data)
                        articles.append(article)
                    
                    except Exception as e:
                        logger.error(f"Failed to scrape article {thumbnail.url}: {e}")
        
        else:
            # Browser client implementation would go here
            pass
        
        logger.info(f"Scraped {len(articles)} articles from {len(thumbnails)} thumbnails")
        
        # Save articles to structured JSONL file
        saved_path = self._storage.save_articles(articles, self.country, self.name)
        if saved_path:
            self._saved_files['articles'] = saved_path
        
        self.scraped_articles = articles
        return articles
    
    async def run_full_scrape(self) -> Dict[str, Any]:
        """
        Run a complete scraping operation.
        
        Returns:
            Dictionary with scraping results and statistics
        """
        logger.info(f"Starting full scrape for {self.name} ({self.country})")
        
        try:
            # Step 1 & 2 Combined: Discover and scrape thumbnails in one pass
            # This ensures each URL is only requested once
            thumbnails = await self.discover_and_scrape_thumbnails()
            
            # Step 3: Scrape full articles
            articles = await self.scrape_articles(thumbnails)
            
            # Compile results
            results = {
                "success": True,
                "newspaper": self.name,
                "country": self.country,
                "statistics": {
                    "thumbnails_found": len(thumbnails),
                    "articles_scraped": len(articles),
                    "failed_urls": len(self.failed_urls),
                    "failed_news": len(self.failed_news)
                },
                "data": {
                    "thumbnails": [
                        {
                            "url": str(thumb.url),
                            "title": thumb.title,
                            "date": thumb.date
                        } for thumb in thumbnails
                    ],
                    "articles": [
                        {
                            "url": str(article.url),
                            "title": article.title,
                            "date": article.date,
                            "body": article.body,
                            "tags": article.tags,
                            "source": article.source,
                            "country": article.country
                        } for article in articles
                    ]
                },
                "errors": self.failed_urls
            }
            
            # Save failed URLs and news if any
            if self.failed_urls:
                saved_path = self._storage.save_failed_urls(self.failed_urls, self.country, self.name)
                if saved_path:
                    self._saved_files['failed_urls'] = saved_path
            
            if self.failed_news:
                saved_path = self._storage.save_failed_news(self.failed_news, self.country, self.name)
                if saved_path:
                    self._saved_files['failed_news'] = saved_path
            
            # Save metadata
            saved_path = self._storage.save_metadata(results, self.country, self.name)
            if saved_path:
                self._saved_files['metadata'] = saved_path
            
            logger.info(f"Scraping completed for {self.name}: {len(articles)} articles scraped")
            return results
            
        except Exception as e:
            logger.error(f"Scraping failed for {self.name}: {e}")
            return {
                "success": False,
                "newspaper": self.name,
                "country": self.country,
                "error": str(e),
                "statistics": {
                    "listing_urls": 0,
                    "thumbnails_found": len(self.scraped_thumbnails),
                    "articles_scraped": len(self.scraped_articles),
                    "failed_urls": len(self.failed_urls),
                    "failed_news": len(self.failed_news)
                }
            }
    
    def cleanup(self):
        """Clean up resources."""
        if self._browser_client:
            self._browser_client.close_driver()
        
        # HTTP client cleanup is handled automatically by httpx
