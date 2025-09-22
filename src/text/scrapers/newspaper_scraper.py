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
        
        # Error tracking
        self.failed_urls: List[Dict[str, Any]] = []
    
    def _get_http_client(self) -> AsyncHttpClient:
        """Get or create HTTP client."""
        if self._http_client is None:
            # Extract domain for cookie management
            domain = urlparse(self.base_url).netloc
            
            # Configure client based on auth settings
            auth_config = self.config.auth or {}
            
            self._http_client = AsyncHttpClient(
                parser="html.parser",  # Default to BeautifulSoup
                domain=domain if auth_config else None,
                timeout=60.0,
                max_concurrent=10,
                rate_limit=0.5  # Be polite to servers
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
        Discover listing pages and scrape thumbnails in a single pass.
        
        This method combines URL discovery and thumbnail scraping to ensure
        each URL is only requested once, improving efficiency.
        
        Returns:
            List of ThumbnailRecord objects
        """
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
                            "error": result.error,
                            "stage": "thumbnail_listing"
                        })
                        continue
                    
                    # Parse the scraped content
                    thumbnail_elements = result.data
                    if not thumbnail_elements:
                        logger.warning(f"No thumbnails found on {result.url}")
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
            thumbnails = await self.scrape_thumbnails(listing_urls)
        
        logger.info(f"Total thumbnails discovered and scraped: {len(thumbnails)}")
        
        # Save thumbnails to JSONL file
        await self._save_thumbnails_to_jsonl(thumbnails)
        
        return thumbnails

    async def _save_thumbnails_to_jsonl(self, thumbnails: List[ThumbnailRecord]) -> None:
        """
        Save thumbnails to JSONL file in the data folder.
        
        Args:
            thumbnails: List of ThumbnailRecord objects to save
        """
        if not thumbnails:
            return
        
        # Get data folder path from environment or use default
        data_folder = Path(os.getenv("DATA_FOLDER_PATH", "data"))
        data_folder.mkdir(parents=True, exist_ok=True)
        
        # Create filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{self.country}_{self.name}_thumbnails_{timestamp}.jsonl"
        filepath = data_folder / filename
        
        # Save thumbnails as JSONL
        with open(filepath, 'w', encoding='utf-8') as f:
            for thumbnail in thumbnails:
                # Convert to dict and keep only essential fields
                thumb_data = {
                    "url": str(thumbnail.url),
                    "title": thumbnail.title,
                    "date": thumbnail.date
                }
                f.write(json.dumps(thumb_data, ensure_ascii=False) + '\n')
        
        logger.info(f"Saved {len(thumbnails)} thumbnails to {filepath}")

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

    async def scrape_thumbnails(self, listing_urls: List[str]) -> List[ThumbnailRecord]:
        """
        Scrape thumbnail data from listing pages.
        
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
                        "error": result.error,
                        "stage": "thumbnail_listing"
                    })
                    continue
                
                # Parse the scraped content
                thumbnail_elements = result.data
                if not thumbnail_elements:
                    logger.warning(f"No thumbnails found on {result.url}")
                    continue
                
                # Extract data from each thumbnail element
                # We need to extract additional data (title, URL, date) from each thumbnail element
                # The thumbnail elements are already extracted, but we need the full page context
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
            # Browser client implementation
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
                            logger.warning(f"No thumbnails found on {url}")
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
    
    async def scrape_articles(self, thumbnails: List[ThumbnailRecord]) -> List[ArticleRecord]:
        """
        Scrape full article content from thumbnail URLs.
        
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
            
            # Scrape articles in batches with progress tracking
            batch_size = 10  # Increased batch size for better performance
            logger.info(f"Scraping {len(article_urls)} articles in batches of {batch_size}")
            
            for i in range(0, len(article_urls), batch_size):
                batch_urls = article_urls[i:i + batch_size]
                
                # Scrape this batch (tqdm progress bar is handled in client.scrape_urls)
                results = await client.scrape_urls(batch_urls, list(article_selectors.values()))
                
                # Process results without verbose logging
                batch_articles = 0
                
                for j, result in enumerate(results):
                    if not result.success:
                        self.failed_urls.append({
                            "url": result.url,
                            "error": result.error,
                            "stage": "article_content"
                        })
                        continue
                    
                    try:
                        # Get corresponding thumbnail
                        thumb_index = i + j
                        if thumb_index < len(thumbnails):
                            thumbnail = thumbnails[thumb_index]
                            
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
                            batch_articles += 1
                    
                    except Exception as e:
                        logger.error(f"Failed to create ArticleRecord: {e}")
                
                # Log batch progress
                logger.info(f"Processed batch {i//batch_size + 1}: {batch_articles} articles, {len(articles)} total")
                
                # Small delay between batches
                await asyncio.sleep(0.5)
        
        else:
            # Browser client implementation would go here
            pass
        
        logger.info(f"Scraped {len(articles)} articles from {len(thumbnails)} thumbnails")
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
                    "failed_urls": len(self.failed_urls)
                },
                "data": {
                    "thumbnails": [thumb.dict() for thumb in thumbnails],
                    "articles": [article.dict() for article in articles]
                },
                "errors": self.failed_urls
            }
            
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
                    "failed_urls": len(self.failed_urls)
                }
            }
    
    def cleanup(self):
        """Clean up resources."""
        if self._browser_client:
            self._browser_client.close_driver()
        
        # HTTP client cleanup is handled automatically by httpx
