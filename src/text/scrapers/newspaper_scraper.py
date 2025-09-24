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
from .parser import extract_thumbnail_data_from_element, extract_article_data_from_soup

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
        
        if self.client_type != "http":
            raise NotImplementedError("Browser client not yet supported for combined discovery/scraping")

        client = self._get_http_client()
        thumbnails = []
        thumbnail_selector = self.selectors["thumbnail"]

        async for result_batch in self.listing_strategy.discover_and_scrape(client, self.base_url, thumbnail_selector):
            for result in result_batch:
                if not result.success:
                    self._add_failed_url(
                        url=result.url,
                        status_code=result.status_code,
                        error=result.error,
                        stage="thumbnail_listing"
                    )
                    continue

                thumbnail_elements = result.data
                if not thumbnail_elements:
                    logger.warning(f"No thumbnails found on {result.url} - starting retry sequence")

                    retry_count = 0
                    max_retries = 25
                    retry_delay = 2.0

                    while retry_count < max_retries:
                        retry_count += 1
                        logger.debug(f"Retry {retry_count}/{max_retries} for {result.url}")
                        await asyncio.sleep(retry_delay)

                        try:
                            retry_result = await client.scrape_url(client._http_client, str(result.url), thumbnail_selector)

                            if retry_result.success and retry_result.data:
                                logger.info(f"Thumbnails found on retry {retry_count} for {result.url}")
                                thumbnail_elements = retry_result.data
                                break

                        except Exception as e:
                            logger.debug(f"Retry {retry_count} failed for {result.url}: {e}")

                    if not thumbnail_elements:
                        logger.warning(f"No thumbnails found after {max_retries} retries for {result.url}")
                        self._add_failed_url(
                            url=result.url,
                            status_code=getattr(result, 'status_code', None),
                            error=f"No thumbnails found after {max_retries} retries",
                            stage="thumbnail_listing_no_content"
                        )
                        continue

                for thumb_elem in thumbnail_elements:
                    thumb_data = extract_thumbnail_data_from_element(
                        thumb_elem,
                        str(result.url),
                        self.selectors,
                        self.base_url,
                        self.config.cleaning
                    )
                    if thumb_data:
                        try:
                            thumbnail = ThumbnailRecord(**thumb_data)
                            thumbnails.append(thumbnail)
                        except Exception as e:
                            logger.error(f"Failed to create ThumbnailRecord: {e}")
                            logger.error(f"Data: {thumb_data}")

            logger.info(f"Processed batch: {len(result_batch)} pages, {len(thumbnails)} total thumbnails")
        
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
                    self._add_failed_url(
                        url=result.url,
                        status_code=result.status_code,
                        error=result.error,
                        stage="thumbnail_listing"
                    )
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
                        self._add_failed_url(
                            url=result.url,
                            status_code=getattr(result, 'status_code', None),
                            error=f"No thumbnails found after {max_retries} retries",
                            stage="thumbnail_listing_no_content"
                        )
                        continue
                
                # Extract data from each thumbnail element
                for thumb_elem in thumbnail_elements:
                    thumb_data = extract_thumbnail_data_from_element(
                        thumb_elem, 
                        str(result.url), 
                        self.selectors, 
                        self.base_url, 
                        self.config.cleaning
                    )
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
                            self._add_failed_url(
                                url=url,
                                error="Failed to navigate",
                                stage="thumbnail_listing"
                            )
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
                                self._add_failed_url(
                                    url=url,
                                    error=f"No thumbnails found after {max_retries} retries",
                                    stage="thumbnail_listing_no_content"
                                )
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
                        self._add_failed_url(
                            url=url,
                            error=str(e),
                            stage="thumbnail_listing"
                        )
            
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
                        # Fetch article page HTML content
                        content, status_code = await client.request_url(http_client, str(thumbnail.url))
                        
                        if content is None:
                            self._add_failed_news(
                                url=thumbnail.url,
                                status_code=status_code,
                                error="Failed to retrieve content",
                                stage="article_content"
                            )
                            continue
                        
                        # Parse the HTML content
                        soup = client.parse_content(content)
                        
                        # Extract article body and tags using the new extraction function
                        article_content = extract_article_data_from_soup(
                            soup, 
                            str(thumbnail.url), 
                            self.selectors, 
                            self.base_url, 
                            self.config.cleaning
                        )
                        
                        # Combine thumbnail data with extracted article content
                        article_data = {
                            "url": str(thumbnail.url),
                            "title": thumbnail.title,
                            "date": thumbnail.date if thumbnail.date else article_content.get("date", ""),
                            "body": article_content.get("body", ""),
                            "tags": article_content.get("tags", []),
                            "source": self.name,
                            "country": self.country
                        }
                        
                        # Apply cleaning functions to article data if configured
                        cleaning_config = self.config.cleaning
                        if cleaning_config:
                            article_data = apply_cleaning(article_data, cleaning_config, self.base_url)
                        
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
            
            # Compile results - ensure all HttpUrl objects are converted to strings
            try:
                logger.info("Creating results dictionary...")
                
                # Serialize thumbnails and articles first
                serialized_thumbnails = []
                for i, thumb in enumerate(thumbnails):
                    try:
                        serialized_thumb = self._storage.serialize_for_json(thumb.dict())
                        serialized_thumbnails.append(serialized_thumb)
                    except Exception as e:
                        logger.error(f"Failed to serialize thumbnail {i}: {e}")
                        logger.error(f"Thumbnail type: {type(thumb)}")
                        logger.error(f"Thumbnail dict keys: {list(thumb.dict().keys()) if hasattr(thumb, 'dict') else 'No dict method'}")
                        raise
                
                serialized_articles = []
                for i, article in enumerate(articles):
                    try:
                        serialized_article = self._storage.serialize_for_json(article.dict())
                        serialized_articles.append(serialized_article)
                    except Exception as e:
                        logger.error(f"Failed to serialize article {i}: {e}")
                        logger.error(f"Article type: {type(article)}")
                        logger.error(f"Article dict keys: {list(article.dict().keys()) if hasattr(article, 'dict') else 'No dict method'}")
                        raise
                
                # Serialize failed URLs
                try:
                    serialized_errors = self._storage.serialize_for_json(self.failed_urls)
                except Exception as e:
                    logger.error(f"Failed to serialize failed_urls: {e}")
                    logger.error(f"Failed URLs count: {len(self.failed_urls)}")
                    for i, failed_url in enumerate(self.failed_urls):
                        logger.error(f"Failed URL {i}: {failed_url}")
                        logger.error(f"Failed URL {i} types: {[(k, type(v)) for k, v in failed_url.items()]}")
                    raise
                
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
                        "thumbnails": serialized_thumbnails,
                        "articles": serialized_articles
                    },
                    "errors": serialized_errors
                }
                
                logger.info("Results dictionary created successfully")
                
            except Exception as e:
                logger.error(f"Failed to create results dictionary: {e}")
                raise
            
            # Save failed URLs and news if any - let storage handle serialization
            if self.failed_urls:
                saved_path = self._storage.save_failed_urls(self.failed_urls, self.country, self.name)
                if saved_path:
                    self._saved_files['failed_urls'] = saved_path
            
            if self.failed_news:
                saved_path = self._storage.save_failed_news(self.failed_news, self.country, self.name)
                if saved_path:
                    self._saved_files['failed_news'] = saved_path
            
            # Save metadata - let storage handle serialization
            try:
                saved_path = self._storage.save_metadata(results, self.country, self.name)
                if saved_path:
                    self._saved_files['metadata'] = saved_path
            except Exception as e:
                logger.error(f"Failed to save metadata: {e}")
                # Debug the structure to find HttpUrl objects
                import json
                logger.error("Debugging results structure:")
                try:
                    json.dumps(results)
                    logger.error("Results are JSON serializable - error might be elsewhere")
                except Exception as json_error:
                    logger.error(f"Results JSON error: {json_error}")
                    # Check each part of results
                    for key, value in results.items():
                        try:
                            json.dumps({key: value})
                            logger.error(f"✓ {key} is serializable")
                        except Exception as part_error:
                            logger.error(f"✗ {key} failed: {part_error}")
                            logger.error(f"  Type: {type(value)}")
                            if isinstance(value, dict):
                                for subkey, subvalue in value.items():
                                    try:
                                        json.dumps({subkey: subvalue})
                                    except:
                                        logger.error(f"    ✗ {subkey}: {type(subvalue)}")
                raise
            
            logger.info(f"Scraping completed for {self.name}: {len(articles)} articles scraped")
            return results
            
        except Exception as e:
            logger.error(f"Scraping failed for {self.name}: {e}")
            error_results = {
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
            # Ensure error results are also JSON serializable
            return self._storage.serialize_for_json(error_results)
    
    async def run_update_scrape(self) -> Dict[str, Any]:
        """
        Run an update scraping operation.
        
        This mode scrapes all URLs but only processes articles that don't already exist
        in the news.jsonl file, making it efficient for incremental updates.
        
        Returns:
            Dictionary with scraping results and statistics
        """
        logger.info(f"Starting update scrape for {self.name} ({self.country})")
        
        try:
            # Step 1: Load existing articles to get URLs we should skip
            existing_urls = self._storage.get_existing_article_urls(self.country, self.name)
            logger.info(f"Found {len(existing_urls)} existing articles to skip")
            
            # Step 2: Discover and scrape thumbnails (same as full scrape)
            thumbnails = await self.discover_and_scrape_thumbnails()
            logger.info(f"Discovered {len(thumbnails)} thumbnails")
            
            # Step 3: Filter thumbnails to only include new articles
            new_thumbnails = []
            skipped_count = 0
            
            for thumbnail in thumbnails:
                thumbnail_url = str(thumbnail.url)
                if thumbnail_url not in existing_urls:
                    new_thumbnails.append(thumbnail)
                else:
                    skipped_count += 1
            
            logger.info(f"Filtered thumbnails: {len(new_thumbnails)} new, {skipped_count} already exist")
            
            # Step 4: Scrape only new articles
            if new_thumbnails:
                new_articles = await self.scrape_articles(new_thumbnails)
                logger.info(f"Scraped {len(new_articles)} new articles")
            else:
                new_articles = []
                logger.info("No new articles to scrape")
            
            # Step 5: If we have new articles, append them to existing file
            if new_articles:
                # Load existing articles
                existing_articles = self._storage.load_existing_articles(self.country, self.name) or []
                
                # Combine existing and new articles
                all_articles = existing_articles + new_articles
                
                # Save combined articles
                saved_path = self._storage.save_articles(all_articles, self.country, self.name)
                if saved_path:
                    self._saved_files['news'] = saved_path
                
                # Save thumbnails (all discovered thumbnails, not just new ones)
                saved_path = self._storage.save_thumbnails_as_urls(thumbnails, self.country, self.name)
                if saved_path:
                    self._saved_files['urls'] = saved_path
            else:
                logger.info("No new articles to save")
            
            # Compile results - ensure all HttpUrl objects are converted to strings
            try:
                logger.info("Creating update results dictionary...")
                
                # Serialize thumbnails and new articles
                serialized_thumbnails = []
                for i, thumb in enumerate(thumbnails):
                    try:
                        serialized_thumb = self._storage.serialize_for_json(thumb.dict())
                        serialized_thumbnails.append(serialized_thumb)
                    except Exception as e:
                        logger.error(f"Failed to serialize thumbnail {i}: {e}")
                        raise
                
                serialized_new_articles = []
                for i, article in enumerate(new_articles):
                    try:
                        serialized_article = self._storage.serialize_for_json(article.dict())
                        serialized_new_articles.append(serialized_article)
                    except Exception as e:
                        logger.error(f"Failed to serialize new article {i}: {e}")
                        raise
                
                # Serialize failed URLs
                try:
                    serialized_errors = self._storage.serialize_for_json(self.failed_urls)
                except Exception as e:
                    logger.error(f"Failed to serialize failed_urls: {e}")
                    raise
                
                results = {
                    "success": True,
                    "newspaper": self.name,
                    "country": self.country,
                    "mode": "update",
                    "statistics": {
                        "thumbnails_found": len(thumbnails),
                        "existing_articles_skipped": skipped_count,
                        "new_articles_scraped": len(new_articles),
                        "total_articles_after_update": len(existing_urls) + len(new_articles),
                        "failed_urls": len(self.failed_urls),
                        "failed_news": len(self.failed_news)
                    },
                    "data": {
                        "thumbnails": serialized_thumbnails,
                        "new_articles": serialized_new_articles
                    },
                    "errors": serialized_errors
                }
                
                logger.info("Update results dictionary created successfully")
                
            except Exception as e:
                logger.error(f"Failed to create update results dictionary: {e}")
                raise
            
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
            try:
                saved_path = self._storage.save_metadata(results, self.country, self.name, metadata_type="update")
                if saved_path:
                    self._saved_files['metadata'] = saved_path
            except Exception as e:
                logger.error(f"Failed to save update metadata: {e}")
                raise
            
            logger.info(f"Update scrape completed for {self.name}: {len(new_articles)} new articles added")
            return results
            
        except Exception as e:
            logger.error(f"Update scraping failed for {self.name}: {e}")
            error_results = {
                "success": False,
                "newspaper": self.name,
                "country": self.country,
                "mode": "update",
                "error": str(e),
                "statistics": {
                    "thumbnails_found": len(self.scraped_thumbnails),
                    "new_articles_scraped": len(self.scraped_articles),
                    "failed_urls": len(self.failed_urls),
                    "failed_news": len(self.failed_news)
                }
            }
            # Ensure error results are also JSON serializable
            return self._storage.serialize_for_json(error_results)
    
    def _add_failed_url(self, url: Any, status_code: Any = None, error: str = None, stage: str = None):
        """
        Safely add a failed URL with automatic serialization of HttpUrl objects.
        
        Args:
            url: URL that failed (can be HttpUrl or string)
            status_code: HTTP status code if available
            error: Error message
            stage: Stage where the failure occurred
        """
        failed_entry = {
            "url": str(url) if url else None,
            "status_code": status_code,
            "error": error,
            "stage": stage
        }
        self.failed_urls.append(failed_entry)
    
    def _add_failed_news(self, url: Any, status_code: Any = None, error: str = None, stage: str = None):
        """
        Safely add a failed news article with automatic serialization of HttpUrl objects.
        
        Args:
            url: URL that failed (can be HttpUrl or string)
            status_code: HTTP status code if available
            error: Error message
            stage: Stage where the failure occurred
        """
        failed_entry = {
            "url": str(url) if url else None,
            "status_code": status_code,
            "error": error,
            "stage": stage
        }
        self.failed_news.append(failed_entry)

    def cleanup(self):
        """Clean up resources."""
        if self._browser_client:
            self._browser_client.close_driver()
        
        # HTTP client cleanup is handled automatically by httpx