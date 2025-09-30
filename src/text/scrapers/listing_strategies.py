"""
Listing discovery strategies for finding article URLs.

This module contains different strategies for discovering article listings
from newspaper websites, including pagination, archives, categories, and search.
"""

import asyncio
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, AsyncGenerator
import logging
from urllib.parse import urljoin
from .client_http import AsyncHttpClient

logger = logging.getLogger(__name__)


class ListingStrategy(ABC):
    """
    Abstract base class for listing discovery strategies.
    
    Each strategy implements a different method for discovering
    article URLs from a newspaper website.
    """
    
    def __init__(self, config: Dict[str, Any], max_pages: Optional[int] = None):
        """
        Initialize the strategy with configuration.

        Args:
            config: Strategy-specific configuration dictionary
            max_pages: Optional limit on the number of pages to discover
        """
        self.config = config
        self.max_pages = max_pages
    
    @abstractmethod
    async def discover_and_scrape(
        self,
        client: AsyncHttpClient,
        base_url: str,
        thumbnail_selector: str
    ) -> AsyncGenerator[List[Any], None]:
        """Discover listing pages and immediately scrape thumbnails."""
        pass


class PaginationStrategy(ListingStrategy):
    """
    Dynamic pagination strategy for sites with numbered pages.
    
    This strategy automatically detects the last page by checking
    batches of URLs until all URLs in a batch return errors.
    """
    
    def __init__(self, config: Dict[str, Any], max_pages: Optional[int] = None):
        """
        Initialize pagination strategy.
        
        Expected config keys:
        - url_template: URL template with {num} placeholder
        - start_page: Starting page number (default: 1)
        - batch_size: Number of pages to check per batch (default: 5)
        - start_url: Optional initial URL to scrape before pagination (default: None)
        """
        super().__init__(config, max_pages)
        
        url_template_config = config["url_template"]
        if isinstance(url_template_config, str):
            self.url_templates = [url_template_config]
        else:
            self.url_templates = url_template_config

        self.start_page = config.get("start_page", 1)
        self.step = config.get("step", 1)
        self.batch_size = config.get("batch_size", 5)
        self.start_url = config.get("start_url", None)

        for template in self.url_templates:
            if "{num}" not in template:
                raise ValueError(
                    f"URL template '{template}' must contain {{num}} placeholder"
                )
    
    def generate_page_urls(self, start_page: int, count: int) -> List[str]:
        """
        Generate a batch of page URLs.
        
        Args:
            start_page: Starting page number
            count: Number of URLs to generate
            
        Returns:
            List of generated URLs
        """
        urls = []
        for template in self.url_templates:
            for i in range(count):
                page_num = start_page + (i * self.step)
                url = template.format(num=page_num)
                urls.append(url)
        return urls
    
    async def discover_and_scrape(
        self,
        client: AsyncHttpClient,
        base_url: str,
        thumbnail_selector: str
    ) -> AsyncGenerator[List, None]:
        """
        Discover URLs and immediately scrape thumbnails in a single request per URL.
        
        If start_url is provided, scrapes it first before starting pagination.
        This method combines discovery and scraping to ensure each URL is only
        requested once, improving efficiency and reducing server load.
        
        Args:
            client: HTTP client for making requests
            base_url: Base URL of the website
            thumbnail_selector: CSS selector for thumbnail elements
            
        Yields:
            Lists of ScrapingResult objects containing thumbnail data
        """
        # Handle start_url if provided
        if self.start_url:
            logger.info(f"Starting with initial URL scraping: {self.start_url}")
            # Scrape the start_url first
            start_results = await client.scrape_urls([self.start_url], thumbnail_selector)
            successful_start_results = [result for result in start_results if result.success]
            
            if successful_start_results:
                logger.info(f"Successfully scraped start URL: {len(successful_start_results)} results")
                yield successful_start_results
            else:
                logger.warning(f"Failed to scrape start URL: {self.start_url}")
        
        current_page = self.start_page
        
        logger.info(f"Starting combined pagination discovery and scraping from page {current_page}")
        
        batch_number = 1
        total_pages_processed = 0
        
        while True:
            # Respect max_pages limit if set
            if self.max_pages is not None and total_pages_processed >= self.max_pages:
                logger.info(
                    f"Reached max_pages limit ({self.max_pages}), stopping pagination."
                )
                break

            # Determine how many pages to fetch in this batch
            pages_to_fetch = self.batch_size
            if self.max_pages is not None:
                remaining_pages = self.max_pages - total_pages_processed
                if remaining_pages < pages_to_fetch:
                    pages_to_fetch = remaining_pages

            if pages_to_fetch <= 0:
                break

            # Generate batch of page URLs
            batch_urls = self.generate_page_urls(current_page, pages_to_fetch)
            
            # Log batch start
            logger.info(f"Processing batch {batch_number}: pages {current_page}-{current_page + self.batch_size - 1}")
            
            # Scrape all URLs in this batch (this will return 404 for non-existent pages)
            scraping_results = await client.scrape_urls(batch_urls, thumbnail_selector)
            
            # Filter successful results (200 status)
            successful_results = [result for result in scraping_results if result.success]
            
            if not successful_results:
                # No successful pages in this batch - we've reached the end
                logger.info(f"Batch {batch_number}: No accessible pages found. Stopping pagination.")
                break
            
            # Update counters
            total_pages_processed += len(successful_results)
            
            # Yield the successful scraping results
            yield successful_results
            
            # Log batch completion
            logger.info(f"Batch {batch_number} completed: {len(successful_results)} pages processed, {total_pages_processed} total pages")
            
            # If we got fewer successful results than the batch size, we might be near the end
            if len(successful_results) < self.batch_size:
                logger.info(f"Batch {batch_number}: Found {len(successful_results)}/{self.batch_size} pages. Might be near end of pagination.")
            
            # Move to next batch
            current_page += self.batch_size * self.step
            batch_number += 1
            
            # Add a small delay between batches for politeness
            await asyncio.sleep(0.5)
        
        logger.info("Combined pagination discovery and scraping completed")


class ArchiveStrategy(ListingStrategy):
    """
    Archive strategy for date-based article discovery.
    
    This strategy iterates through date-based archive pages
    (e.g., /2025/01/, /2025/02/) to discover articles.
    """
    
    def __init__(self, config: Dict[str, Any], max_pages: Optional[int] = None):
        """
        Initialize archive strategy.
        
        Expected config keys:
        - url_template: URL template with {year} and/or {month} placeholders
        - start_date: Start date (YYYY-MM-DD format)
        - end_date: End date (YYYY-MM-DD format, optional)
        - date_format: Date format for URL ('monthly' or 'daily')
        - batch_size: Number of archive URLs to check per batch (optional, default 10)
        """
        super().__init__(config, max_pages)
        
        self.url_template = config["url_template"]
        self.date_format = config.get("date_format", "monthly")
        self.batch_size = int(config.get("batch_size", 10))
        if self.batch_size <= 0:
            raise ValueError("batch_size must be a positive integer")

        # Parse start date and normalise based on date format
        self.start_date = datetime.strptime(config["start_date"], "%Y-%m-%d")
        if self.date_format == "monthly":
            self.start_date = self.start_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        else:
            self.start_date = self.start_date.replace(hour=0, minute=0, second=0, microsecond=0)

        # Determine end date – default to current period if not supplied
        end_date_str = config.get("end_date")
        if end_date_str:
            end_date = datetime.strptime(end_date_str, "%Y-%m-%d")
        else:
            end_date = datetime.now()

        if self.date_format == "monthly":
            end_date = end_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        else:
            end_date = end_date.replace(hour=0, minute=0, second=0, microsecond=0)

        if end_date < self.start_date:
            raise ValueError("end_date must not be earlier than start_date")

        self.end_date = end_date
        
        # Validate template placeholders
        required_placeholders = []
        if self.date_format == "monthly":
            required_placeholders = ["{year}", "{month}"]
        elif self.date_format == "daily":
            required_placeholders = ["{year}", "{month}", "{day}"]
        
        for placeholder in required_placeholders:
            if placeholder not in self.url_template:
                raise ValueError(f"url_template must contain {placeholder} placeholder")
    
    def generate_date_urls(self) -> List[str]:
        """
        Generate archive URLs based on date range.
        
        Returns:
            List of archive URLs
        """
        urls = []
        current_date = self.start_date
        
        while current_date <= self.end_date:
            if self.date_format == "monthly":
                url = self.url_template.format(
                    year=current_date.year,
                    month=current_date.month
                )
                # Move to next month
                if current_date.month == 12:
                    current_date = current_date.replace(year=current_date.year + 1, month=1)
                else:
                    current_date = current_date.replace(month=current_date.month + 1)
            
            elif self.date_format == "daily":
                url = self.url_template.format(
                    year=current_date.year,
                    month=current_date.month,
                    day=current_date.day
                )
                # Move to next day
                current_date += timedelta(days=1)
            
            urls.append(url)
        
        return urls
    
    async def discover_and_scrape(
        self,
        client: AsyncHttpClient,
        base_url: str,
        thumbnail_selector: str
    ) -> AsyncGenerator[List, None]:
        """Discover archive pages and scrape thumbnails in a single pass."""
        archive_urls = self.generate_date_urls()

        # If max_pages is set, take the most recent N pages
        if self.max_pages is not None and len(archive_urls) > self.max_pages:
            logger.info(
                f"Truncating archive URLs from {len(archive_urls)} to {self.max_pages} (most recent)"
            )
            archive_urls = archive_urls[-self.max_pages :]
        logger.info(
            f"Generated {len(archive_urls)} archive URLs from {self.start_date.date()} to {self.end_date.date()}"
        )

        batch_number = 1

        for i in range(0, len(archive_urls), self.batch_size):
            batch = archive_urls[i:i + self.batch_size]
            logger.info(
                f"Processing archive batch {batch_number}: {len(batch)} URLs"
            )

            scraping_results = await client.scrape_urls(batch, thumbnail_selector)
            successful_results = [result for result in scraping_results if result.success]

            if successful_results:
                yield successful_results
            else:
                logger.info(f"Archive batch {batch_number} returned no accessible pages")

            batch_number += 1
            await asyncio.sleep(0.5)



def create_listing_strategy(
    config: Dict[str, Any], max_pages: Optional[int] = None
) -> ListingStrategy:
    """
    Factory function to create a listing strategy based on configuration.
    
    Args:
        config: Strategy configuration dictionary
        
    Returns:
        Appropriate ListingStrategy instance
        
    Raises:
        ValueError: If strategy type is unknown
    """
    strategy_type = config.get("type")
    
    if strategy_type == "pagination":
        return PaginationStrategy(config, max_pages=max_pages)
    elif strategy_type == "archive":
        return ArchiveStrategy(config, max_pages=max_pages)
    elif strategy_type == "category":
        return CategoryStrategy(config, max_pages=max_pages)
    elif strategy_type == "search":
        return SearchStrategy(config, max_pages=max_pages)
    else:
        raise ValueError(f"Unknown listing strategy type: {strategy_type}")
