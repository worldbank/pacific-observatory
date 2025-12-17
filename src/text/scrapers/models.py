"""
Pydantic models for data validation and schema enforcement.

This module defines the data schemas used throughout the scraping system
to ensure consistency and data quality.
"""

from datetime import date, datetime
from typing import List, Optional, Union, Any
from pydantic import BaseModel, HttpUrl, field_validator, Field, ConfigDict


class ThumbnailRecord(BaseModel):
    """
    Model for article thumbnail/listing data.
    
    This represents the basic information extracted from article listings
    or archive pages before scraping the full article content.
    """
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    url: HttpUrl = Field(..., description="Full URL to the article")
    title: str = Field(..., min_length=1, description="Article title")
    date: Optional[str] = Field(default=None, description="Publication date as string")

    @field_validator('title')
    @classmethod
    def title_must_not_be_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError('Title cannot be empty or whitespace only')
        return v.strip()

    @field_validator('date', mode='before')
    @classmethod
    def parse_date(cls, v: Any) -> Optional[str]:
        """Parse various date formats into YYYY-MM-DD format."""
        if v is None:
            return None
        if isinstance(v, date):
            return v.isoformat()
        if isinstance(v, datetime):
            return v.date().isoformat()
        if isinstance(v, str):
            if v.strip():
                from .pipelines.cleaning import handle_mixed_dates
                return handle_mixed_dates(v.strip())
        return None


class ArticleRecord(BaseModel):
    """
    Model for individual article data.
    
    Represents the full scraped content of a single article.
    """
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    url: HttpUrl = Field(..., description="Full URL to the article")
    title: str = Field(..., min_length=1, description="Article title")
    date: str = Field(..., description="Publication date in YYYY-MM-DD format")
    body: str = Field(..., min_length=1, description="Full article text content")
    tags: Optional[List[str]] = Field(default_factory=list, description="Article tags/categories")
    source: str = Field(..., description="Name of the news source")
    country: str = Field(..., description="Country identifier (can be any string)")
    
    @field_validator('title', 'body', 'source')
    @classmethod
    def text_fields_must_not_be_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError('Text fields cannot be empty or whitespace only')
        return v.strip()
    
    @field_validator('country')
    @classmethod
    def country_must_not_be_empty(cls, v: str) -> str:
        """Validate that country is not empty."""
        if not v or not v.strip():
            raise ValueError('Country cannot be empty')
        return v.strip()
    
    @field_validator('tags', mode='before')
    @classmethod
    def parse_tags(cls, v: Any) -> List[str]:
        """Ensure tags is always a list."""
        if v is None:
            return []
        if isinstance(v, str):
            # Split comma-separated tags
            return [tag.strip() for tag in v.split(',') if tag.strip()]
        if isinstance(v, list):
            return [str(tag).strip() for tag in v if str(tag).strip()]
        return []
    
    @field_validator('date', mode='before')
    @classmethod
    def parse_date(cls, v: Any) -> str:
        """Parse various date formats into YYYY-MM-DD format."""
        if isinstance(v, date):
            return v.isoformat()
        if isinstance(v, datetime):
            return v.date().isoformat()
        if isinstance(v, str):
            # Try to normalize string dates to YYYY-MM-DD format
            if v.strip():
                # Import here to avoid circular imports
                from .pipelines.cleaning import handle_mixed_dates
                return handle_mixed_dates(v.strip())
            return ""
        if v is None:
            return ""
        return str(v)


class ScrapingResult(BaseModel):
    """
    Model for scraping operation results.
    
    This wraps the scraped data with metadata about the scraping operation.
    """
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    success: bool = Field(..., description="Whether the scraping was successful")
    data: Optional[Any] = None  # Simplified to avoid complex Union types
    error: Optional[str] = None
    status_code: Optional[int] = Field(default=None, description="HTTP status code if available")
    url: Optional[HttpUrl] = None
    timestamp: datetime = Field(default_factory=datetime.now)
    
    @field_validator('error')
    @classmethod
    def error_when_not_success(cls, v: Optional[str], info) -> Optional[str]:
        """Ensure error is provided when success is False."""
        if hasattr(info, 'data') and not info.data.get('success', True) and not v:
            raise ValueError('Error message must be provided when success is False')
        return v


SelectorType = Union[str, List[str]]


class ThumbnailSelectorConfig(BaseModel):
    """Configuration for thumbnail/listing selectors."""
    model_config = ConfigDict(arbitrary_types_allowed=True)

    container: SelectorType = Field(..., description="Selector(s) for thumbnail container elements")
    title: SelectorType = Field(..., description="Selector(s) for thumbnail titles")
    url: SelectorType = Field(..., description="Selector(s) for thumbnail URLs")
    date: Optional[SelectorType] = Field(default=None, description="Optional selector(s) for thumbnail dates")


class ArticleSelectorConfig(BaseModel):
    """Configuration for article-level selectors."""
    model_config = ConfigDict(arbitrary_types_allowed=True)

    body: SelectorType = Field(..., description="Selector(s) for article body content")
    date: Optional[SelectorType] = Field(default=None, description="Optional selector(s) for article dates")
    tags: Optional[SelectorType] = Field(default=None, description="Optional selector(s) for article tags")


class SelectorsConfig(BaseModel):
    """Structured selector configuration grouping thumbnail and article selectors."""
    thumbnail: ThumbnailSelectorConfig
    article: ArticleSelectorConfig


class NewspaperConfig(BaseModel):
    """
    Model for newspaper configuration validation.
    
    This validates the YAML configuration files used to define
    newspaper-specific scraping parameters.
    """
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    name: str = Field(..., description="Human-readable newspaper name")
    country: str = Field(..., description="Country identifier (can be any string)")
    base_url: HttpUrl = Field(..., description="Base URL of the newspaper website")
    
    # Listing configuration
    listing: dict = Field(..., description="Listing discovery configuration")
    
    # Selectors for data extraction
    selectors: SelectorsConfig = Field(..., description="Structured selectors for data extraction")
    
    # Optional configurations
    auth: Optional[dict] = Field(default=None, description="Authentication configuration")
    cleaning: Optional[dict] = Field(default=None, description="Data cleaning configuration")
    headers: Optional[dict] = Field(default=None, description="Custom HTTP headers")
    client: str = Field(default="http", description="Client type: 'http' or 'browser'")
    concurrency: Optional[int] = Field(default=10, description="Maximum concurrent requests for HTTP client")
    rate_limit: Optional[float] = Field(default=0.1, description="Minimum delay between requests in seconds")
    retries: Optional[int] = Field(default=3, description="Number of retry attempts for failed requests")
    retry_seconds: Optional[float] = Field(default=2.0, description="Wait time in seconds between retry attempts")
    
    # Test/debug options
    max_pages: Optional[int] = Field(default=None, description="Maximum number of listing pages to scrape")
    max_articles: Optional[int] = Field(default=None, description="Maximum number of articles to scrape")
    
    @field_validator('country')
    @classmethod
    def country_must_not_be_empty(cls, v: str) -> str:
        """Validate that country is not empty."""
        if not v or not v.strip():
            raise ValueError('Country cannot be empty')
        return v.strip()
    
    @field_validator('client')
    @classmethod
    def client_must_be_valid(cls, v: str) -> str:
        """Validate client type."""
        if v not in ['http', 'browser']:
            raise ValueError('Client must be either "http" or "browser"')
        return v
    
    @field_validator('concurrency')
    @classmethod
    def concurrency_must_be_positive(cls, v: Optional[int]) -> Optional[int]:
        """Validate concurrency is a positive integer."""
        if v is not None and v <= 0:
            raise ValueError('Concurrency must be a positive integer')
        return v
    
    @field_validator('headers')
    @classmethod
    def headers_must_be_string_dict(cls, v: Optional[dict]) -> Optional[dict]:
        """Validate headers are string key-value pairs."""
        if v is not None:
            if not isinstance(v, dict):
                raise ValueError('Headers must be a dictionary')
            for key, value in v.items():
                if not isinstance(key, str) or not isinstance(value, str):
                    raise ValueError('Headers must have string keys and values')
        return v
    
    @field_validator('retries')
    @classmethod
    def retries_must_be_non_negative(cls, v: Optional[int]) -> Optional[int]:
        """Validate retries is a non-negative integer."""
        if v is not None and v < 0:
            raise ValueError('Retries must be a non-negative integer')
        return v
    
    @field_validator('retry_seconds')
    @classmethod
    def retry_seconds_must_be_positive(cls, v: Optional[float]) -> Optional[float]:
        """Validate retry_seconds is a positive number."""
        if v is not None and v <= 0:
            raise ValueError('Retry seconds must be a positive number')
        return v
    
    @field_validator('listing')
    @classmethod
    def listing_must_have_type(cls, v: dict) -> dict:
        """Validate listing configuration has required fields."""
        if 'type' not in v:
            raise ValueError('Listing configuration must specify a type')
        if v['type'] not in ['pagination', 'archive', 'api']:
            raise ValueError('Listing type must be one of: pagination, archive, category, search')
        return v
