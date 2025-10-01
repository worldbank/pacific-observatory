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
    Clean SIBC date format and normalize to YYYY-MM-DD format.
    
    Args:
        date_str: Raw date string from SIBC
        
    Returns:
        Normalized date string in YYYY-MM-DD format
    """
    if not date_str:
        return ""
    
    # Use the handle_mixed_dates function to normalize to YYYY-MM-DD
    return handle_mixed_dates(date_str)


def handle_mixed_dates(date_str: str) -> str:
    """
    Handle mixed date formats and normalize them with robust cleaning.
    
    This function handles various date formats and common formatting issues
    found in scraped content, including prefixes, suffixes, and extra text.
    
    Args:
        date_str: Date string in various formats
        
    Returns:
        Normalized date string in YYYY-MM-DD format
    """
    if not date_str:
        return ""
    
    # Initial cleanup
    cleaned = date_str.strip()
    
    # Remove common prefixes and suffixes that appear in scraped dates
    # This handles cases like "- September 24, 2025", "• Sep 24, 2025", "| Date: ..."
    cleaned = re.sub(r'^[-•\*\+\|\s]+', '', cleaned).strip()
    cleaned = re.sub(r'[-•\*\+\|\s]+$', '', cleaned).strip()
    
    # Remove common date-related prefixes (case insensitive)
    cleaned = re.sub(r'^(Published|Posted|Date|On|Updated|Last\s+modified|Modified):\s*', '', cleaned, flags=re.IGNORECASE).strip()
    
    # Remove "By [Author]" patterns that might precede dates
    cleaned = re.sub(r'^By\s+[^,]+,?\s*', '', cleaned, flags=re.IGNORECASE).strip()
    
    # Remove HTML entities and extra whitespace
    import html
    cleaned = html.unescape(cleaned)
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    
    if not cleaned:
        return ""
    
    # Try to parse and normalize to ISO format
    try:
        # Comprehensive date patterns (most specific first)
        patterns = [
            # ISO and standard formats
            "%Y-%m-%d",                    # 2025-09-24
            "%Y/%m/%d",                    # 2025/09/24
            "%d/%m/%Y",                    # 24/09/2025
            "%m/%d/%Y",                    # 09/24/2025
            "%d-%m-%Y",                    # 24-09-2025
            "%m-%d-%Y",                    # 09-24-2025
            
            # Full month names with various formats
            "%B %d, %Y",                   # September 24, 2025
            "%b %d, %Y",                   # Sep 24, 2025
            "%d %B %Y",                    # 24 September 2025
            "%d %b %Y",                    # 24 Sep 2025
            "%B %d %Y",                    # September 24 2025 (no comma)
            "%b %d %Y",                    # Sep 24 2025 (no comma)
            
            # With day names
            "%A, %B %d, %Y",               # Monday, September 24, 2025
            "%A %B %d, %Y",                # Monday September 24, 2025
            "%a, %B %d, %Y",               # Mon, September 24, 2025
            "%a %B %d, %Y",                # Mon September 24, 2025
            "%A, %b %d, %Y",               # Monday, Sep 24, 2025
            "%A %b %d, %Y",                # Monday Sep 24, 2025
            
            # With times
            "%B %d, %Y %H:%M",             # September 24, 2025 14:30
            "%b %d, %Y %H:%M",             # Sep 24, 2025 14:30
            "%B %d, %Y %H:%M:%S",          # September 24, 2025 14:30:45
            "%b %d, %Y %H:%M:%S",          # Sep 24, 2025 14:30:45
            "%Y-%m-%dT%H:%M:%S",           # ISO datetime format
            "%Y-%m-%d %H:%M:%S",           # Standard datetime format
            "%Y-%m-%dT%H:%M:%SZ",          # ISO datetime with Z
            "%Y-%m-%dT%H:%M:%S.%fZ",       # ISO datetime with microseconds
            
            # Alternative formats
            "%d.%m.%Y",                    # 24.09.2025
            "%m.%d.%Y",                    # 09.24.2025
            "%Y.%m.%d",                    # 2025.09.24
            "%d-%b-%Y",                    # 24-Sep-2025
            "%d-%B-%Y",                    # 24-September-2025
        ]
        
        for pattern in patterns:
            try:
                parsed_date = datetime.strptime(cleaned, pattern)
                return parsed_date.strftime("%Y-%m-%d")
            except ValueError:
                continue
        
        # Fallback: Try to extract date using regex patterns
        # This handles cases where there's extra text around the date
        date_patterns = [
            # Match "Month DD, YYYY" patterns
            r'(\w+\s+\d{1,2},?\s+\d{4})',
            # Match "DD Month YYYY" patterns  
            r'(\d{1,2}\s+\w+\s+\d{4})',
            # Match "YYYY-MM-DD" patterns
            r'(\d{4}[-/]\d{1,2}[-/]\d{1,2})',
            # Match "MM/DD/YYYY" or "DD/MM/YYYY" patterns
            r'(\d{1,2}[/-]\d{1,2}[/-]\d{4})',
        ]
        
        for regex_pattern in date_patterns:
            match = re.search(regex_pattern, cleaned)
            if match:
                date_part = match.group(1).strip()
                
                # Try to parse the extracted date part
                for strp_pattern in patterns:
                    try:
                        parsed_date = datetime.strptime(date_part, strp_pattern)
                        # logger.info(f"Successfully parsed date using regex fallback: '{date_str}' -> '{parsed_date.strftime('%Y-%m-%d')}'")
                        return parsed_date.strftime("%Y-%m-%d")
                    except ValueError:
                        continue
        
        # If still no match, log warning and return cleaned string
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
            if not paragraphs:
                paragraphs = content_element.find_all("div")
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


def clean_sibc_body(body_text: str) -> str:
    """
    Clean SIBC article body by removing author bylines.
    
    SIBC articles often start with author bylines like "By Aaron Szetu in Gizo, Western Province".
    This function removes paragraphs that start with "By " to clean the article content.
    
    Args:
        body_text: Raw article body text
        
    Returns:
        Cleaned article body text with author bylines removed
    """
    if not body_text:
        return ""
    
    # Split the text into sentences/paragraphs (assuming they're separated by periods and spaces)
    # or by common paragraph separators
    paragraphs = []
    
    # Try to split by common paragraph separators first
    if '. ' in body_text:
        # Split by '. ' but be careful not to split abbreviations
        parts = body_text.split('. ')
        for i, part in enumerate(parts):
            if i < len(parts) - 1:  # Add the period back except for the last part
                part = part + '.'
            paragraphs.append(part.strip())
    else:
        # If no clear paragraph separation, treat as single paragraph
        paragraphs = [body_text.strip()]
    
    # Filter out paragraphs that start with "By "
    cleaned_paragraphs = []
    for paragraph in paragraphs:
        if paragraph and not paragraph.startswith("By "):
            cleaned_paragraphs.append(paragraph)
    
    # Join the remaining paragraphs back together
    cleaned_text = ' '.join(cleaned_paragraphs).strip()
    
    return cleaned_text


def clean_solomon_times_date(date_str: str, **kwargs) -> str:
    """
    Clean Solomon Times date format.
    
    For thumbnails: Extract dates from archive URL paths like:
    "https://www.solomontimes.com/news/latest/2024/05" -> "2024-05-01"
    
    For articles: Parse date from article content using standard date parsing.
    
    Args:
        date_str: Raw date string (may be empty for URL-based extraction)
        **kwargs: Additional context including 'page_url' for URL-based extraction
        
    Returns:
        Standardized date string (YYYY-MM-DD format)
    """
    # Check if we have a page_url in kwargs for URL-based extraction
    page_url = kwargs.get('page_url') or kwargs.get('url')
    
    # If we have a page URL and it's an archive URL, extract date from path
    if page_url and '/news/latest/' in page_url:
        try:
            # Extract year/month from URL path like the original scraper
            # Original: date = "-".join(i for i in page[0].split("/")[-2:])
            path_parts = page_url.rstrip('/').split('/')
            if len(path_parts) >= 2:
                year = path_parts[-2]
                month = path_parts[-1]
                
                # Validate year and month
                if year.isdigit() and month.isdigit():
                    year_int = int(year)
                    month_int = int(month)
                    
                    if 2000 <= year_int <= 2030 and 1 <= month_int <= 12:
                        # Return first day of the month in YYYY-MM-DD format
                        return f"{year_int:04d}-{month_int:02d}-01"
        except Exception as e:
            logger.warning(f"Could not extract date from Solomon Times URL '{page_url}': {e}")
    
    # If no URL or URL extraction failed, try to parse date_str from article content
    if date_str and date_str.strip():
        try:
            import pandas as pd
            # Use pandas "mixed" format like the original scraper
            parsed_date = pd.to_datetime(date_str, format="mixed")
            return parsed_date.strftime("%Y-%m-%d")
        except Exception as e:
            logger.warning(f"Could not parse Solomon Times date '{date_str}': {e}")
            # Fallback to handle_mixed_dates function
            return handle_mixed_dates(date_str)
    
    # If we still don't have a date and we have a page URL, try to extract from any URL
    if page_url:
        try:
            # Try to extract date from any URL pattern
            path_parts = page_url.rstrip('/').split('/')
            for i in range(len(path_parts) - 1):
                year = path_parts[i]
                month = path_parts[i + 1]
                
                if year.isdigit() and month.isdigit():
                    year_int = int(year)
                    month_int = int(month)
                    
                    if 2000 <= year_int <= 2030 and 1 <= month_int <= 12:
                        return f"{year_int:04d}-{month_int:02d}-01"
        except Exception as e:
            logger.debug(f"Could not extract date from any URL pattern '{page_url}': {e}")
    
    return ""


def clean_solomon_times_content(content_element) -> str:
    """
    Clean Solomon Times article content.
    
    Extracts and cleans text from article body elements, similar to the original scraper
    which extracted content from "article-body" selectors.
    
    Args:
        content_element: BeautifulSoup element containing article content
        
    Returns:
        Cleaned content string
    """
    if not content_element:
        return ""
    
    try:
        if hasattr(content_element, 'get_text'):
            # Extract all text from the element
            text = content_element.get_text(separator=' ', strip=True)
            return clean_html_text(text)
        elif hasattr(content_element, 'find_all'):
            # If it's a container, extract text from paragraphs
            paragraphs = content_element.find_all(['p', 'div'])
            if paragraphs:
                content_parts = [p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True)]
                return " ".join(content_parts)
            else:
                # Fallback to getting all text
                text = content_element.get_text(separator=' ', strip=True)
                return clean_html_text(text)
        else:
            # If it's already text, clean it
            return clean_html_text(str(content_element))
    except Exception as e:
        logger.error(f"Error cleaning Solomon Times content: {e}")
        return clean_html_text(str(content_element))


def clean_solomon_times_tags(tags_element) -> str:
    """
    Clean Solomon Times tags/categories.
    
    Extracts and joins tag text from tag elements, similar to the original scraper
    which processed "tags" selectors.
    
    Args:
        tags_element: BeautifulSoup element containing tag links
        
    Returns:
        Comma-separated tags string
    """
    if not tags_element:
        return ""
    
    try:
        if hasattr(tags_element, 'find_all'):
            # Look for links within the tags element
            links = tags_element.find_all("a")
            if links:
                # Join link text with commas, filtering out empty tags
                tag_parts = [link.get_text(strip=True) for link in links if link.get_text(strip=True)]
                return ", ".join(tag_parts)
            else:
                # If no links, try to get text directly
                text = tags_element.get_text(strip=True)
                return clean_html_text(text) if text else ""
        else:
            # If it's already text, return cleaned version
            return clean_html_text(str(tags_element))
    except Exception as e:
        logger.error(f"Error cleaning Solomon Times tags: {e}")
        return clean_html_text(str(tags_element))


def clean_matangi_url(url: str, base_url: str = None) -> Optional[str]:
    """
    Resolve the final article URL for Matangi Tonga by following the 'print' link.

    Matangi Tonga articles are on a separate print-friendly page, so this function
    scrapes the initial URL to find the print URL.

    Args:
        url: The initial article URL from the listing page
        base_url: The base URL for resolving relative links

    Returns:
        The absolute URL to the print-friendly article page, or None if not found
    """
    if not url:
        return None

    import httpx
    from bs4 import BeautifulSoup
    from urllib.parse import urljoin

    try:
        # Ensure URL is absolute
        absolute_url = urljoin(base_url, url) if base_url and not url.startswith('http') else url

        # Scrape the initial article page to find the print link
        with httpx.Client() as client:
            response = client.get(absolute_url, follow_redirects=True)
            response.raise_for_status()

        soup = BeautifulSoup(response.content, "html.parser")
        print_link = soup.select_one(".print-page a, .node-main-content .print a")

        if print_link and print_link.get("href"):
            print_url = print_link["href"]
            # Ensure the print URL is absolute
            final_url = urljoin(base_url, print_url) if base_url else print_url
            logger.info(f"Resolved Matangi URL: {url} -> {final_url}")
            return final_url
        else:
            logger.warning(f"No print link found for Matangi URL: {url}")
            # Fallback to the original URL if no print link is found
            return absolute_url

    except Exception as e:
        logger.error(f"Failed to resolve Matangi print URL for {url}: {e}")
        return None


def filter_abc_au_articles(record: dict) -> bool:
    """
    Filter out non-article content from ABC AU API results.

    Args:
        record: The record dictionary extracted from the API.

    Returns:
        True if the record is an article, False otherwise.
    """
    # The media type is derived from the contentUri field
    content_uri = record.get("contentUri", "")
    if content_uri:
        media_type = content_uri.split("//")[-1].split("/")[0]
        if media_type == "article":
            return True
    return False


def filter_samoa_observer_premium(record: dict) -> bool:
    """
    Filter out premium articles from Samoa Observer.
    
    Args:
        record: The record dictionary extracted from the API.
        
    Returns:
        True if the article should be kept, False otherwise.
    """
    if record.get("is_premium") is True:
        return False
    return True


def normalize_date(date_str: str) -> str:
    """
    Normalize any date string to YYYY-MM-DD format.
    
    This is a general-purpose date normalization function that can be used
    by any newspaper configuration to ensure consistent date formatting.
    
    Args:
        date_str: Date string in any supported format
        
    Returns:
        Normalized date string in YYYY-MM-DD format
    """
    return handle_mixed_dates(date_str)

def join_body_list(body_text_list: list) -> str:
    """
    Join body text from a list of strings.
    
    Args:
        body_text_list: List of strings to join
        
    Returns:
        Joined string
    """
    return " ".join([s.strip() for s in body_text_list])

# Registry of available cleaning functions
CLEANING_FUNCTIONS = {
    'clean_sibc_date': clean_sibc_date,
    'clean_sibc_body': clean_sibc_body,
    'clean_solomon_star_date': clean_solomon_star_date,
    'clean_solomon_star_content': clean_solomon_star_content,
    'clean_solomon_star_tags': clean_solomon_star_tags,
    'clean_solomon_times_date': clean_solomon_times_date,
    'clean_solomon_times_content': clean_solomon_times_content,
    'clean_solomon_times_tags': clean_solomon_times_tags,
    'handle_mixed_dates': handle_mixed_dates,
    'normalize_date': normalize_date,
    'clean_html_text': clean_html_text,
    'normalize_tags': normalize_tags,
    'clean_url': clean_url,
    'clean_title': clean_title,
    'clean_matangi_url': clean_matangi_url,
    'filter_samoa_observer_premium': filter_samoa_observer_premium,
    'filter_abc_au_articles': filter_abc_au_articles,
    'join_body_list': join_body_list,
    }


def get_cleaning_func(function_name: str):
    """
    Get a cleaning function by name.
    
    Args:
        function_name: Name of the cleaning function
        
    Returns:
        Cleaning function or None if not found
    """
    return CLEANING_FUNCTIONS.get(function_name)


def apply_cleaning(data: Any, cleaning_config: dict, base_url: str = None, page_url: str = None, **kwargs) -> Any:
    """
    Apply cleaning functions to data based on configuration.
    
    Args:
        data: Data dictionary to clean
        cleaning_config: Dictionary mapping field names to cleaning function names
        base_url: Base URL for URL cleaning
        page_url: Page URL for context-aware cleaning (e.g., date extraction from URLs)
        **kwargs: Additional context for cleaning functions
        
    Returns:
        Cleaned data dictionary
    """
    if not cleaning_config or not isinstance(data, dict):
        return data
    
    cleaned_data = data.copy()
    
    for field_name, function_name in cleaning_config.items():
        if field_name in cleaned_data:
            cleaning_func = get_cleaning_func(function_name)
            if cleaning_func:
                try:
                    # Special handling for functions that need additional context
                    if function_name == 'clean_url' and base_url:
                        cleaned_data[field_name] = cleaning_func(cleaned_data[field_name], base_url)
                    elif function_name == 'clean_solomon_times_date':
                        # Pass page URL context for Solomon Times date extraction
                        cleaned_data[field_name] = cleaning_func(
                            cleaned_data[field_name], 
                            page_url=page_url, 
                            base_url=base_url,
                            **kwargs
                        )
                    elif function_name == 'clean_matangi_url':
                        cleaned_data[field_name] = cleaning_func(cleaned_data[field_name], base_url=base_url)
                    else:
                        cleaned_data[field_name] = cleaning_func(cleaned_data[field_name])
                except Exception as e:
                    logger.error(f"Error applying cleaning function '{function_name}' to field '{field_name}': {e}")
            else:
                logger.warning(f"Cleaning function '{function_name}' not found")
    
    return cleaned_data
