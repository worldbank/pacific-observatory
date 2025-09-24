"""
Content parsing functions for newspaper scraping.

This module contains functions for extracting structured data from HTML content,
including thumbnail data from listing pages and article content from individual pages.
"""

import logging
from typing import Dict, Any, Optional
from urllib.parse import urljoin
from .pipelines.cleaning import apply_cleaning

logger = logging.getLogger(__name__)


def extract_thumbnail_data_from_element(
    thumbnail_element, 
    page_url: str, 
    selectors: Dict[str, str], 
    base_url: str, 
    cleaning_config: Optional[Dict[str, str]] = None
) -> Optional[Dict[str, Any]]:
    """
    Extract thumbnail data directly from a thumbnail element.
    
    Args:
        thumbnail_element: Individual thumbnail element (BeautifulSoup element)
        page_url: URL of the page this element came from
        selectors: Dictionary of CSS selectors for data extraction
        base_url: Base URL for making relative URLs absolute
        cleaning_config: Optional cleaning configuration
        
    Returns:
        Dictionary with extracted data or None if extraction failed
    """
    try:
        data = {}
        
        # Extract title
        title_selector = selectors.get("title")
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
        url_selector = selectors.get("url")
        if url_selector:
            if url_selector.endswith("::attr(href)"):
                # CSS selector with href extraction
                selector = url_selector.replace("::attr(href)", "")
                url_elem = thumbnail_element.select_one(selector)
                if url_elem:
                    href = url_elem.get("href")
                    # Make URL absolute
                    data["url"] = urljoin(base_url, href) if href else None
            else:
                # Regular CSS selector - assume it's a link
                url_elem = thumbnail_element.select_one(url_selector)
                if url_elem:
                    href = url_elem.get("href")
                    data["url"] = urljoin(base_url, href) if href else None
        
        # Extract date
        date_selector = selectors.get("date")
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
        if cleaning_config:
            data = apply_cleaning(data, cleaning_config, base_url)
        
        return data
        
    except Exception as e:
        logger.error(f"Error extracting thumbnail data: {e}")
        return None


def extract_article_data_from_soup(
    soup, 
    article_url: str, 
    selectors: Dict[str, str], 
    base_url: str, 
    cleaning_config: Optional[Dict[str, str]] = None
) -> Dict[str, Any]:
    """
    Extract article body and tags from a BeautifulSoup object.
    
    Args:
        soup: BeautifulSoup object of the article page
        article_url: URL of the article page
        selectors: Dictionary of CSS selectors for data extraction
        base_url: Base URL for making relative URLs absolute
        cleaning_config: Optional cleaning configuration
        
    Returns:
        Dictionary with extracted article data (body, tags)
    """
    try:
        data = {}
        
        # Extract article body
        body_selector = selectors.get("article_body")
        if body_selector:
            if body_selector.endswith("::text"):
                # CSS selector with text extraction
                selector = body_selector.replace("::text", "")
                body_elements = soup.select(selector)
                if body_elements:
                    # Join all paragraph texts with spaces
                    body_texts = [elem.get_text(strip=True) for elem in body_elements if elem.get_text(strip=True)]
                    data["body"] = " ".join(body_texts)
                else:
                    data["body"] = ""
            else:
                # Regular CSS selector
                body_elements = soup.select(body_selector)
                if body_elements:
                    body_texts = [elem.get_text(strip=True) for elem in body_elements if elem.get_text(strip=True)]
                    data["body"] = " ".join(body_texts)
                else:
                    data["body"] = ""
        else:
            data["body"] = ""
        
        # Extract tags
        tags_selector = selectors.get("tags")
        if tags_selector:
            if tags_selector.endswith("::text"):
                # CSS selector with text extraction
                selector = tags_selector.replace("::text", "")
                tag_elements = soup.select(selector)
                if tag_elements:
                    tags = [elem.get_text(strip=True) for elem in tag_elements if elem.get_text(strip=True)]
                    data["tags"] = tags
                else:
                    data["tags"] = []
            else:
                # Regular CSS selector
                tag_elements = soup.select(tags_selector)
                if tag_elements:
                    tags = [elem.get_text(strip=True) for elem in tag_elements if elem.get_text(strip=True)]
                    data["tags"] = tags
                else:
                    data["tags"] = []
        else:
            data["tags"] = []
        
        # Apply cleaning functions if configured
        if cleaning_config:
            data = apply_cleaning(data, cleaning_config, base_url)
        
        return data
        
    except Exception as e:
        logger.error(f"Error extracting article data from {article_url}: {e}")
        return {"body": "", "tags": []}
