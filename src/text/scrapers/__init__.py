"""
Refactored newspaper scraping framework.

This package has been decomposed into specialized modules following
the config-driven architecture specified in the PRD.

The old monolithic classes have been moved to:
- client_http.py: AsyncHttpClient (evolved from RequestsScraper)
- client_browser.py: BrowserClient (evolved from SeleniumScraper)
- newspaper_scraper.py: NewspaperScraper (evolved from NewspaperScraper)
- models.py: Pydantic data models
- listing_strategies.py: Listing discovery strategies
- factory.py: Factory functions for creating scrapers from config
- pipelines/: Data processing and storage
- orchestration/: Scripts for running scrapers

For backward compatibility, you can still import the main classes:
"""

# Import main classes for backward compatibility
from .client_http import AsyncHttpClient
from .client_browser import BrowserClient
from .newspaper_scraper import NewspaperScraper
from .models import ThumbnailRecord, ArticleRecord, NewspaperConfig
from .factory import create_scraper, create_scraper_from_file
from .pipelines.storage import CSVStorage

# Legacy aliases for backward compatibility
RequestsScraper = AsyncHttpClient  # Note: This is now async
SeleniumScraper = BrowserClient

__all__ = [
    "AsyncHttpClient",
    "BrowserClient",
    "NewspaperScraper",
    "ThumbnailRecord",
    "ArticleRecord",
    "NewspaperConfig",
    "create_scraper",
    "create_scraper_from_file",
    "CSVStorage",
    # Legacy aliases
    "RequestsScraper",
    "SeleniumScraper",
]
