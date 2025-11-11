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
        previous_batch_urls = set()
        
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
            current_batch_urls = set(batch_urls)
            
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
            
            retrieved_thumbnails = sum([len(result.data) for result in successful_results])
            if retrieved_thumbnails == 0:
                logger.info(f"Batch {batch_number}: No thumbnails found. Stopping pagination.")
                break

            # Check if current batch URLs are the same as previous batch
            if current_batch_urls == previous_batch_urls:
                logger.info(f"Batch {batch_number}: Batch URLs identical to previous batch. Stopping pagination.")
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
            
            # Store current batch URLs for next iteration comparison
            previous_batch_urls = current_batch_urls
            
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
                    month=f"{current_date.month:02d}"
                )
                # Move to next month
                if current_date.month == 12:
                    current_date = current_date.replace(year=current_date.year + 1, month=1)
                else:
                    current_date = current_date.replace(month=current_date.month + 1)
            
            elif self.date_format == "daily":
                url = self.url_template.format(
                    year=current_date.year,
                    month=f"{current_date.month:02d}",
                    day=f"{current_date.day:02d}"
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


class ApiStrategy(ListingStrategy):
    """
    API strategy for JSON-based article discovery.
    
    This strategy fetches article listings from JSON API endpoints
    instead of scraping HTML pages. Supports both offset-based and
    page-based pagination.
    """
    
    def __init__(self, config: Dict[str, Any], max_pages: Optional[int] = None):
        """
        Initialize API strategy.
        
        Expected config keys:
        - url_template: API URL template(s) with placeholders like {offset}, {size}, {page}
        - pagination_type: "offset" or "page"
        - offset_start: Starting offset (for offset-based, default: 0)
        - offset_step: Offset increment (for offset-based, default: 100)
        - page_start: Starting page number (for page-based, default: 0)
        - page_step: Page increment (for page-based, default: 1)
        - json_paths: Dictionary mapping field names to JSON paths
        """
        super().__init__(config, max_pages)
        
        url_template_config = config["url_template"]
        if isinstance(url_template_config, str):
            self.url_templates = [url_template_config]
        else:
            self.url_templates = url_template_config
        
        self.pagination_type = config.get("pagination_type", "page")
        self.offset_start = config.get("offset_start", 0)
        self.offset_step = config.get("offset_step", 100)
        self.page_start = config.get("page_start", 0)
        self.page_step = config.get("page_step", 1)
        self.json_paths = config.get("json_paths", {})
        self.batch_size = config.get("batch_size", 10)
        self.exclude = config.get('exclude', None)
        
        # Validate pagination type
        if self.pagination_type not in ["offset", "page"]:
            raise ValueError(f"pagination_type must be 'offset' or 'page', got: {self.pagination_type}")
    
    def _get_nested_value(self, data: Dict, path: str) -> Any:
        """
        Get a value from nested dictionaries/lists using dot notation.

        Supports list traversal by aggregating values when a key resolves to a
        list of dictionaries. Numeric keys are treated as list indices.

        Args:
            data: Dictionary to extract from
            path: Dot-separated path (e.g., "pagination.total" or "tags.slug")

        Returns:
            Extracted value(s) or None if the path cannot be resolved
        """
        if not path:
            return data

        keys = path.split(".")
        current_values = [data]

        for key in keys:
            next_values = []

            for value in current_values:
                if isinstance(value, dict):
                    if key in value and value[key] is not None:
                        next_values.append(value[key])
                elif isinstance(value, list):
                    # Numeric access: treat key as index
                    if key.isdigit():
                        idx = int(key)
                        if 0 <= idx < len(value):
                            next_values.append(value[idx])
                        continue

                    # Non-numeric key: apply to each element in the list
                    for item in value:
                        if isinstance(item, dict):
                            if key in item and item[key] is not None:
                                next_values.append(item[key])
                        elif isinstance(item, list):
                            # Preserve nested lists for further traversal
                            next_values.append(item)

            if not next_values:
                return None

            current_values = next_values

        if len(current_values) == 1:
            return current_values[0]

        return current_values

    def _extract_thumbnails_from_json(self, json_data: Dict, api_url: str) -> List[Dict[str, Any]]:
        """
        Extract thumbnail data from JSON response.

        Args:
            json_data: Parsed JSON response
            api_url: API URL for logging

        Returns:
            List of thumbnail dictionaries
        """
        thumbnails = []
        
        # Get the collection/array of articles
        collection_path = self.json_paths.get("collection", "")
        if collection_path:
            articles = self._get_nested_value(json_data, collection_path)
        else:
            # Assume the root is the collection
            articles = json_data if isinstance(json_data, list) else []
        
        if not articles:
            logger.warning(f"No articles found in API response from {api_url}")
            return thumbnails

        # Extract data from each article
        for article in articles:
            try:
                thumbnail_data = {}

                # Extract each configured field
                for field, path in self.json_paths.items():
                    if field in ["collection", "total"]:
                        continue  # Skip metadata fields

                    value = self._get_nested_value(article, path) if path else None
                    thumbnail_data[field] = value

                if thumbnail_data:
                    thumbnails.append(thumbnail_data)

            except Exception as e:
                logger.error(f"Error extracting thumbnail from article in {api_url}: {e}")
                continue

        return thumbnails

    def _filter_excluded_thumbnails(self, thumbnails: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove thumbnails that match any configured exclusion condition."""
        if not self.exclude:
            return thumbnails

        filtered: List[Dict[str, Any]] = []

        for thumb in thumbnails:
            keep = True

            for condition in self.exclude:
                if not isinstance(condition, dict):
                    continue

                if all(thumb.get(key) == expected for key, expected in condition.items()):
                    keep = False
                    break

            if keep:
                filtered.append(thumb)

        excluded_count = len(thumbnails) - len(filtered)
        if excluded_count:
            logger.info(
                f"Excluded {excluded_count} API records based on 'exclude' filters"
            )

        return filtered
    
    async def discover_and_scrape(
        self,
        client: AsyncHttpClient,
        base_url: str,
        thumbnail_selector: str
    ) -> AsyncGenerator[List[Dict[str, Any]], None]:
        """
        Discover and fetch article listings from API endpoints.
        
        Note: thumbnail_selector is not used for API strategy since we parse JSON.
        """
        import json
        
        for url_template in self.url_templates:
            logger.info(f"Starting API discovery for template: {url_template}")
            
            if self.pagination_type == "offset":
                # Offset-based pagination
                current_offset = self.offset_start
                total_articles = None
                pages_scraped = 0
                
                while True:
                    # Check max_pages limit
                    if self.max_pages and pages_scraped >= self.max_pages:
                        logger.info(f"Reached max_pages limit: {self.max_pages}")
                        break
                    
                    # Generate API URL with current offset
                    api_url = url_template.format(
                        offset=current_offset,
                        size=self.offset_step
                    )
                    
                    try:
                        # Fetch JSON response
                        import httpx
                        async with httpx.AsyncClient() as http_client:
                            content, status_code = await client.request_url(http_client, api_url)
                        
                        if content is None:
                            logger.warning(f"Failed to fetch API URL: {api_url}")
                            break
                        
                        # Parse JSON
                        json_data = json.loads(content)
                        
                        # Get total count if available (first request only)
                        if total_articles is None:
                            total_path = self.json_paths.get("total")
                            if total_path:
                                total_articles = self._get_nested_value(json_data, total_path)
                                logger.info(f"API reports {total_articles} total articles")
                        
                        # Extract thumbnails from JSON
                        thumbnails = self._extract_thumbnails_from_json(json_data, api_url)
                        
                        if not thumbnails:
                            logger.info(f"No more articles found at offset {current_offset}")
                            break
                        
                        thumbnails = self._filter_excluded_thumbnails(thumbnails)
                        logger.info(f"Extracted {len(thumbnails)} articles from offset {current_offset}")
                        yield thumbnails
                        
                        # Increment offset by the step size
                        current_offset += self.offset_step
                        if total_articles and current_offset >= total_articles:
                            logger.info(f"Reached end of articles (offset {current_offset} >= total {total_articles})")
                            break
                        
                        pages_scraped += 1
                        await asyncio.sleep(0.5)
                        
                    except json.JSONDecodeError as e:
                        logger.error(f"Failed to parse JSON from {api_url}: {e}")
                        break
                    except Exception as e:
                        logger.error(f"Error fetching API URL {api_url}: {e}")
                        break
            
            else:
                # Page-based pagination
                current_page = self.page_start
                pages_scraped = 0
                
                while True:
                    # Check max_pages limit
                    if self.max_pages and pages_scraped >= self.max_pages:
                        logger.info(f"Reached max_pages limit: {self.max_pages}")
                        break
                    
                    # Generate API URL with current page
                    api_url = url_template.format(page=current_page)
                    
                    try:
                        # Fetch JSON response
                        import httpx
                        async with httpx.AsyncClient() as http_client:
                            content, status_code = await client.request_url(http_client, api_url)
                        
                        if content is None:
                            logger.warning(f"Failed to fetch API URL: {api_url}")
                            break
                        
                        # Parse JSON
                        json_data = json.loads(content)
                        
                        # Extract thumbnails from JSON
                        thumbnails = self._extract_thumbnails_from_json(json_data, api_url)
                        
                        if not thumbnails:
                            logger.info(f"No more articles found at page {current_page}")
                            break
                        

                        thumbnails = self._filter_excluded_thumbnails(thumbnails)
                        logger.info(f"Extracted {len(thumbnails)} articles from page {current_page}")
                        yield thumbnails
                        
                        current_page += self.page_step
                        pages_scraped += 1
                        await asyncio.sleep(0.5)
                        
                    except json.JSONDecodeError as e:
                        logger.error(f"Failed to parse JSON from {api_url}: {e}")
                        break
                    except Exception as e:
                        logger.error(f"Error fetching API URL {api_url}: {e}")
                        break


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
    elif strategy_type == "api":
        return ApiStrategy(config, max_pages=max_pages)
    else:
        raise ValueError(f"Unknown listing strategy type: {strategy_type}")
