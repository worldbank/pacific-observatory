"""
Listing discovery strategies for finding article URLs.

This module contains different strategies for discovering article listings
from newspaper websites, including pagination, archives, categories, and search.
"""

import asyncio
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Generator, AsyncGenerator
import logging
from urllib.parse import urljoin
from .client_http import AsyncHttpClient
from .client_browser import BrowserClient

logger = logging.getLogger(__name__)


class ListingStrategy(ABC):
    """
    Abstract base class for listing discovery strategies.
    
    Each strategy implements a different method for discovering
    article URLs from a newspaper website.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the strategy with configuration.
        
        Args:
            config: Strategy-specific configuration dictionary
        """
        self.config = config
    
    @abstractmethod
    async def discover_urls(
        self,
        client: AsyncHttpClient,
        base_url: str
    ) -> AsyncGenerator[List[str], None]:
        """
        Discover article URLs using this strategy.
        
        Args:
            client: HTTP client for making requests
            base_url: Base URL of the newspaper
            
        Yields:
            Batches of discovered URLs
        """
        pass


class PaginationStrategy(ListingStrategy):
    """
    Dynamic pagination strategy for sites with numbered pages.
    
    This strategy automatically detects the last page by checking
    batches of URLs until all URLs in a batch return errors.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize pagination strategy.
        
        Expected config keys:
        - url_template: URL template with {num} placeholder
        - start_page: Starting page number (default: 1)
        - step: Page increment step (default: 1)
        - batch_size: Number of pages to check per batch (default: 5)
        """
        super().__init__(config)
        
        self.url_template = config["url_template"]
        self.start_page = config.get("start_page", 1)
        self.step = config.get("step", 1)
        self.batch_size = config.get("batch_size", 5)
        
        if "{num}" not in self.url_template:
            raise ValueError("url_template must contain {num} placeholder")
    
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
        for i in range(count):
            page_num = start_page + (i * self.step)
            url = self.url_template.format(num=page_num)
            urls.append(url)
        return urls
    
    async def discover_urls(
        self,
        client: AsyncHttpClient,
        base_url: str
    ) -> AsyncGenerator[List[str], None]:
        """
        Discover URLs using dynamic pagination.
        
        Generates batches of page URLs and stops when an entire
        batch returns terminal errors (e.g., 404 Not Found).
        """
        current_page = self.start_page
        
        logger.info(f"Starting pagination discovery from page {current_page}")
        
        while True:
            # Generate batch of page URLs
            batch_urls = self.generate_page_urls(current_page, self.batch_size)
            
            logger.debug(f"Checking batch: pages {current_page} to {current_page + (self.batch_size - 1) * self.step}")
            
            # Check if URLs in this batch are accessible
            url_status = await client.check_urls_batch(batch_urls)
            
            # Count successful URLs in this batch
            successful_urls = [url for url, success in url_status.items() if success]
            
            if not successful_urls:
                # No successful URLs in this batch - we've reached the end
                logger.info(f"No accessible pages found in batch starting at page {current_page}. Stopping pagination.")
                break
            
            # Yield the successful URLs for processing
            yield successful_urls
            
            # If we got fewer successful URLs than the batch size, we might be near the end
            if len(successful_urls) < self.batch_size:
                logger.info(f"Found {len(successful_urls)}/{self.batch_size} accessible pages. Might be near end of pagination.")
            
            # Move to next batch
            current_page += self.batch_size * self.step
            
            # Add a small delay between batches for politeness
            await asyncio.sleep(0.5)
        
        logger.info("Pagination discovery completed")


class ArchiveStrategy(ListingStrategy):
    """
    Archive strategy for date-based article discovery.
    
    This strategy iterates through date-based archive pages
    (e.g., /2025/01/, /2025/02/) to discover articles.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize archive strategy.
        
        Expected config keys:
        - url_template: URL template with {year} and/or {month} placeholders
        - start_date: Start date (YYYY-MM-DD format)
        - end_date: End date (YYYY-MM-DD format, optional)
        - date_format: Date format for URL ('monthly' or 'daily')
        """
        super().__init__(config)
        
        self.url_template = config["url_template"]
        self.start_date = datetime.strptime(config["start_date"], "%Y-%m-%d")
        self.end_date = datetime.strptime(
            config.get("end_date", datetime.now().strftime("%Y-%m-%d")),
            "%Y-%m-%d"
        )
        self.date_format = config.get("date_format", "monthly")
        
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
    
    async def discover_urls(
        self,
        client: AsyncHttpClient,
        base_url: str
    ) -> AsyncGenerator[List[str], None]:
        """
        Discover URLs using archive pages.
        """
        archive_urls = self.generate_date_urls()
        
        logger.info(f"Generated {len(archive_urls)} archive URLs from {self.start_date.date()} to {self.end_date.date()}")
        
        # Process archive URLs in batches
        batch_size = 10  # Process 10 archive pages at a time
        
        for i in range(0, len(archive_urls), batch_size):
            batch = archive_urls[i:i + batch_size]
            
            # Check which archive URLs are accessible
            url_status = await client.check_urls_batch(batch)
            successful_urls = [url for url, success in url_status.items() if success]
            
            if successful_urls:
                yield successful_urls
            
            # Small delay between batches
            await asyncio.sleep(0.5)


class CategoryStrategy(ListingStrategy):
    """
    Category strategy for section-based article discovery.
    
    This strategy discovers articles from specific category or
    section pages (e.g., /politics/, /sports/, /business/).
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize category strategy.
        
        Expected config keys:
        - categories: List of category paths or full URLs
        - url_template: Optional URL template with {category} placeholder
        """
        super().__init__(config)
        
        self.categories = config["categories"]
        self.url_template = config.get("url_template")
        
        if not isinstance(self.categories, list):
            raise ValueError("categories must be a list")
    
    def generate_category_urls(self, base_url: str) -> List[str]:
        """
        Generate category URLs.
        
        Args:
            base_url: Base URL of the newspaper
            
        Returns:
            List of category URLs
        """
        urls = []
        
        for category in self.categories:
            if category.startswith("http"):
                # Full URL provided
                urls.append(category)
            elif self.url_template:
                # Use template
                url = self.url_template.format(category=category)
                urls.append(url)
            else:
                # Append to base URL
                url = urljoin(base_url.rstrip("/") + "/", category.lstrip("/"))
                urls.append(url)
        
        return urls
    
    async def discover_urls(
        self,
        client: AsyncHttpClient,
        base_url: str
    ) -> AsyncGenerator[List[str], None]:
        """
        Discover URLs using category pages.
        """
        category_urls = self.generate_category_urls(base_url)
        
        logger.info(f"Processing {len(category_urls)} category pages")
        
        # Check which category URLs are accessible
        url_status = await client.check_urls_batch(category_urls)
        successful_urls = [url for url, success in url_status.items() if success]
        
        if successful_urls:
            yield successful_urls


class SearchStrategy(ListingStrategy):
    """
    Search strategy for query-based article discovery.
    
    This strategy uses the website's search functionality
    to discover articles based on specific queries.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize search strategy.
        
        Expected config keys:
        - url_template: Search URL template with {query} placeholder
        - queries: List of search queries
        - date_range: Optional date range for search results
        """
        super().__init__(config)
        
        self.url_template = config["url_template"]
        self.queries = config["queries"]
        self.date_range = config.get("date_range")
        
        if "{query}" not in self.url_template:
            raise ValueError("url_template must contain {query} placeholder")
        
        if not isinstance(self.queries, list):
            raise ValueError("queries must be a list")
    
    def generate_search_urls(self) -> List[str]:
        """
        Generate search URLs for all queries.
        
        Returns:
            List of search URLs
        """
        urls = []
        
        for query in self.queries:
            # URL encode the query
            import urllib.parse
            encoded_query = urllib.parse.quote_plus(query)
            
            url = self.url_template.format(query=encoded_query)
            
            # Add date range if specified
            if self.date_range:
                # This would need to be customized per site
                # For now, just append the URL as-is
                pass
            
            urls.append(url)
        
        return urls
    
    async def discover_urls(
        self,
        client: AsyncHttpClient,
        base_url: str
    ) -> AsyncGenerator[List[str], None]:
        """
        Discover URLs using search queries.
        """
        search_urls = self.generate_search_urls()
        
        logger.info(f"Processing {len(search_urls)} search queries")
        
        # Check which search URLs are accessible
        url_status = await client.check_urls_batch(search_urls)
        successful_urls = [url for url, success in url_status.items() if success]
        
        if successful_urls:
            yield successful_urls


def create_listing_strategy(config: Dict[str, Any]) -> ListingStrategy:
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
        return PaginationStrategy(config)
    elif strategy_type == "archive":
        return ArchiveStrategy(config)
    elif strategy_type == "category":
        return CategoryStrategy(config)
    elif strategy_type == "search":
        return SearchStrategy(config)
    else:
        raise ValueError(f"Unknown listing strategy type: {strategy_type}")
