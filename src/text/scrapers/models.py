"""
Pydantic models for data validation and schema enforcement.

This module defines the data schemas used throughout the scraping system
to ensure consistency and data quality.
"""

from datetime import date, datetime
from typing import List, Optional, Union
from pydantic import BaseModel, HttpUrl, validator, Field


class ThumbnailRecord(BaseModel):
    """
    Model for article thumbnail/listing data.
    
    This represents the basic information extracted from article listings
    or archive pages before scraping the full article content.
    """
    url: HttpUrl = Field(..., description="Full URL to the article")
    title: str = Field(..., min_length=1, description="Article title")
    date: Union[date, str] = Field(..., description="Publication date")
    
    @validator('title')
    def title_must_not_be_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Title cannot be empty or whitespace only')
        return v.strip()
    
    @validator('date', pre=True)
    def parse_date(cls, v):
        """Parse various date formats into a standardized format."""
        if isinstance(v, date):
            return v
        if isinstance(v, datetime):
            return v.date()
        if isinstance(v, str):
            # Return as string for now - can be processed by cleaning functions
            return v.strip()
        raise ValueError(f'Invalid date format: {v}')


class ArticleRecord(BaseModel):
    """
    Model for complete article data.
    
    This represents the full article information after scraping
    the individual article pages.
    """
    url: HttpUrl = Field(..., description="Full URL to the article")
    title: str = Field(..., min_length=1, description="Article title")
    date: Union[date, str] = Field(..., description="Publication date")
    body: str = Field(..., min_length=1, description="Full article text content")
    tags: Optional[List[str]] = Field(default_factory=list, description="Article tags/categories")
    source: str = Field(..., description="Name of the news source")
    country: str = Field(..., description="Country code (ISO 3166-1 alpha-2)")
    
    @validator('title', 'body', 'source')
    def text_fields_must_not_be_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Text fields cannot be empty or whitespace only')
        return v.strip()
    
    @validator('country')
    def country_must_be_valid_code(cls, v):
        """Validate that country is a 2-letter code."""
        if not v or len(v.strip()) != 2:
            raise ValueError('Country must be a 2-letter ISO code')
        return v.strip().upper()
    
    @validator('tags', pre=True)
    def parse_tags(cls, v):
        """Ensure tags is always a list."""
        if v is None:
            return []
        if isinstance(v, str):
            # Split comma-separated tags
            return [tag.strip() for tag in v.split(',') if tag.strip()]
        if isinstance(v, list):
            return [str(tag).strip() for tag in v if str(tag).strip()]
        return []
    
    @validator('date', pre=True)
    def parse_date(cls, v):
        """Parse various date formats into a standardized format."""
        if isinstance(v, date):
            return v
        if isinstance(v, datetime):
            return v.date()
        if isinstance(v, str):
            # Return as string for now - can be processed by cleaning functions
            return v.strip()
        raise ValueError(f'Invalid date format: {v}')


class ScrapingResult(BaseModel):
    """
    Model for scraping operation results.
    
    This wraps the scraped data with metadata about the scraping operation.
    """
    success: bool = Field(..., description="Whether the scraping was successful")
    data: Optional[Union[ThumbnailRecord, ArticleRecord, List[ThumbnailRecord], List[ArticleRecord]]] = None
    error: Optional[str] = None
    url: Optional[HttpUrl] = None
    timestamp: datetime = Field(default_factory=datetime.now)
    
    @validator('error')
    def error_when_not_success(cls, v, values):
        """Ensure error is provided when success is False."""
        if not values.get('success', True) and not v:
            raise ValueError('Error message must be provided when success is False')
        return v


class NewspaperConfig(BaseModel):
    """
    Model for newspaper configuration validation.
    
    This validates the YAML configuration files used to define
    newspaper-specific scraping parameters.
    """
    name: str = Field(..., description="Human-readable newspaper name")
    country: str = Field(..., description="Country code (ISO 3166-1 alpha-2)")
    base_url: HttpUrl = Field(..., description="Base URL of the newspaper website")
    
    # Listing configuration
    listing: dict = Field(..., description="Listing discovery configuration")
    
    # Selectors for data extraction
    selectors: dict = Field(..., description="CSS/XPath selectors for data extraction")
    
    # Optional configurations
    auth: Optional[dict] = Field(default=None, description="Authentication configuration")
    cleaning: Optional[dict] = Field(default=None, description="Data cleaning configuration")
    client: str = Field(default="http", description="Client type: 'http' or 'browser'")
    
    @validator('country')
    def country_must_be_valid_code(cls, v):
        """Validate that country is a 2-letter code."""
        if not v or len(v.strip()) != 2:
            raise ValueError('Country must be a 2-letter ISO code')
        return v.strip().upper()
    
    @validator('client')
    def client_must_be_valid(cls, v):
        """Validate client type."""
        if v not in ['http', 'browser']:
            raise ValueError('Client must be either "http" or "browser"')
        return v
    
    @validator('listing')
    def listing_must_have_type(cls, v):
        """Validate listing configuration has required fields."""
        if 'type' not in v:
            raise ValueError('Listing configuration must specify a type')
        if v['type'] not in ['pagination', 'archive', 'category', 'search']:
            raise ValueError('Listing type must be one of: pagination, archive, category, search')
        return v
    
    @validator('selectors')
    def selectors_must_have_required_fields(cls, v):
        """Validate selectors have minimum required fields."""
        required_fields = ['thumbnail', 'title', 'url', 'date']
        missing_fields = [field for field in required_fields if field not in v]
        if missing_fields:
            raise ValueError(f'Selectors missing required fields: {missing_fields}')
        return v
