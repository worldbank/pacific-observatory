"""
Data cleaning functions for scraped content.

This module contains cleaning functions that can be referenced
in newspaper configuration files to normalize extracted data.
"""

import re
from datetime import datetime
from typing import Any, Optional
import logging

logger = logging.getLogger(__name__)


def clean_sibc_date(date_str: str) -> str:
    """
    Clean SIBC date format by removing dashes and extra whitespace.
    
    Args:
        date_str: Raw date string from SIBC
        
    Returns:
        Cleaned date string
    """
    if not date_str:
        return ""
    
    # Remove dashes and strip whitespace as done in original scraper
    cleaned = date_str.replace("-", "").strip()
    return cleaned


def handle_mixed_dates(date_str: str) -> str:
    """
    Handle mixed date formats and normalize them.
    
    Args:
        date_str: Date string in various formats
        
    Returns:
        Normalized date string (ISO format if possible)
    """
    if not date_str:
        return ""
    
    # Clean common issues
    cleaned = date_str.strip()
    
    # Try to parse and normalize to ISO format
    try:
        # Common date patterns
        patterns = [
            "%Y-%m-%d",
            "%d/%m/%Y", 
            "%m/%d/%Y",
            "%d-%m-%Y",
            "%Y/%m/%d",
            "%B %d, %Y",
            "%b %d, %Y",
            "%d %B %Y",
            "%d %b %Y"
        ]
        
        for pattern in patterns:
            try:
                parsed_date = datetime.strptime(cleaned, pattern)
                return parsed_date.strftime("%Y-%m-%d")
            except ValueError:
                continue
        
        # If no pattern matches, return cleaned string
        logger.warning(f"Could not parse date format: {date_str}")
        return cleaned
        
    except Exception as e:
        logger.error(f"Error cleaning date '{date_str}': {e}")
        return cleaned


def clean_html_text(text: str) -> str:
    """
    Clean HTML text by removing extra whitespace and HTML artifacts.
    
    Args:
        text: Raw text that may contain HTML artifacts
        
    Returns:
        Cleaned text
    """
    if not text:
        return ""
    
    # Remove HTML entities
    import html
    text = html.unescape(text)
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Strip leading/trailing whitespace
    text = text.strip()
    
    return text


def normalize_tags(tags_str: str) -> list:
    """
    Normalize tag strings into a list of clean tags.
    
    Args:
        tags_str: Comma-separated or other delimited tag string
        
    Returns:
        List of cleaned tag strings
    """
    if not tags_str:
        return []
    
    # Split on common delimiters
    delimiters = [',', ';', '|', '\n']
    tags = [tags_str]
    
    for delimiter in delimiters:
        new_tags = []
        for tag in tags:
            new_tags.extend(tag.split(delimiter))
        tags = new_tags
    
    # Clean each tag
    cleaned_tags = []
    for tag in tags:
        cleaned = tag.strip()
        if cleaned and cleaned not in cleaned_tags:
            cleaned_tags.append(cleaned)
    
    return cleaned_tags


def clean_url(url: str, base_url: str = None) -> str:
    """
    Clean and normalize URLs.
    
    Args:
        url: Raw URL
        base_url: Base URL for making relative URLs absolute
        
    Returns:
        Cleaned, absolute URL
    """
    if not url:
        return ""
    
    url = url.strip()
    
    # Make relative URLs absolute
    if base_url and not url.startswith(('http://', 'https://')):
        from urllib.parse import urljoin
        url = urljoin(base_url, url)
    
    return url


def clean_title(title: str) -> str:
    """
    Clean article titles by removing extra whitespace and common artifacts.
    
    Args:
        title: Raw title text
        
    Returns:
        Cleaned title
    """
    if not title:
        return ""
    
    # Remove extra whitespace
    title = re.sub(r'\s+', ' ', title)
    
    # Remove common title artifacts
    title = title.strip(' -|•')
    
    return title


def clean_solomon_star_date(date_str: str) -> str:
    """
    Clean Solomon Star date format.
    
    Handles pandas "mixed" format parsing that was used in the original scraper:
    urls_df["date"] = pd.to_datetime(urls_df["date"], format="mixed")
    
    Args:
        date_str: Raw date string from Solomon Star
        
    Returns:
        Standardized date string (YYYY-MM-DD format)
    """
    if not date_str:
        return ""
    
    try:
        import pandas as pd
        # Replicate the original pandas "mixed" format processing
        parsed_date = pd.to_datetime(date_str, format="mixed")
        return parsed_date.strftime("%Y-%m-%d")
    except Exception as e:
        logger.warning(f"Could not parse Solomon Star date '{date_str}': {e}")
        # Fallback to handle_mixed_dates function
        return handle_mixed_dates(date_str)


def clean_solomon_star_content(content_element) -> str:
    """
    Clean Solomon Star article content.
    
    Replicates the original scraper logic:
    text = " ".join(p.text for p in text_entry.find_all("p"))
    
    Args:
        content_element: BeautifulSoup element containing article content
        
    Returns:
        Cleaned content string with paragraphs joined by spaces
    """
    if not content_element:
        return ""
    
    try:
        if hasattr(content_element, 'find_all'):
            paragraphs = content_element.find_all("p")
            # Join paragraph text with spaces, filtering out empty paragraphs
            content_parts = [p.text.strip() for p in paragraphs if p.text.strip()]
            return " ".join(content_parts)
        else:
            # If it's already text, clean it
            return clean_html_text(str(content_element))
    except Exception as e:
        logger.error(f"Error cleaning Solomon Star content: {e}")
        return clean_html_text(str(content_element))


def clean_solomon_star_tags(tags_element) -> str:
    """
    Clean Solomon Star tags/categories.
    
    Replicates the original scraper logic:
    tag = ", ".join(p.text for p in tag_entry.find_all("a"))
    
    Args:
        tags_element: BeautifulSoup element containing category links
        
    Returns:
        Comma-separated tags string
    """
    if not tags_element:
        return ""
    
    try:
        if hasattr(tags_element, 'find_all'):
            links = tags_element.find_all("a")
            # Join link text with commas, filtering out empty tags
            tag_parts = [link.text.strip() for link in links if link.text.strip()]
            return ", ".join(tag_parts)
        else:
            # If it's already text, return cleaned version
            return clean_html_text(str(tags_element))
    except Exception as e:
        logger.error(f"Error cleaning Solomon Star tags: {e}")
        return clean_html_text(str(tags_element))


# Registry of available cleaning functions
CLEANING_FUNCTIONS = {
    'clean_sibc_date': clean_sibc_date,
    'clean_solomon_star_date': clean_solomon_star_date,
    'clean_solomon_star_content': clean_solomon_star_content,
    'clean_solomon_star_tags': clean_solomon_star_tags,
    'handle_mixed_dates': handle_mixed_dates,
    'clean_html_text': clean_html_text,
    'normalize_tags': normalize_tags,
    'clean_url': clean_url,
    'clean_title': clean_title
}


def get_cleaning_function(function_name: str):
    """
    Get a cleaning function by name.
    
    Args:
        function_name: Name of the cleaning function
        
    Returns:
        Cleaning function or None if not found
    """
    return CLEANING_FUNCTIONS.get(function_name)


def apply_cleaning(data: Any, cleaning_config: dict, base_url: str = None) -> Any:
    """
    Apply cleaning functions to data based on configuration.
    
    Args:
        data: Data dictionary to clean
        cleaning_config: Dictionary mapping field names to cleaning function names
        base_url: Base URL for URL cleaning
        
    Returns:
        Cleaned data dictionary
    """
    if not cleaning_config or not isinstance(data, dict):
        return data
    
    cleaned_data = data.copy()
    
    for field_name, function_name in cleaning_config.items():
        if field_name in cleaned_data:
            cleaning_func = get_cleaning_function(function_name)
            if cleaning_func:
                try:
                    if function_name == 'clean_url' and base_url:
                        cleaned_data[field_name] = cleaning_func(cleaned_data[field_name], base_url)
                    else:
                        cleaned_data[field_name] = cleaning_func(cleaned_data[field_name])
                except Exception as e:
                    logger.error(f"Error applying cleaning function '{function_name}' to field '{field_name}': {e}")
            else:
                logger.warning(f"Cleaning function '{function_name}' not found")
    
    return cleaned_data
