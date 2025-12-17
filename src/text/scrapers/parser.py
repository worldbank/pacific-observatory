"""
Content parsing functions for newspaper scraping.

This module contains functions for extracting structured data from HTML content,
including thumbnail data from listing pages and article content from individual pages.
"""

import logging
from typing import Dict, Any, Optional, List
from urllib.parse import urljoin
from .pipelines.cleaning import apply_cleaning
from .models import ThumbnailSelectorConfig, ArticleSelectorConfig
import unicodedata

logger = logging.getLogger(__name__)


def extract_with_selector_fallback(
    root,
    selector_config: Optional[Any],
    *,
    first_only: bool = False,
    strip: bool = True,
) -> Dict[str, Any]:
    """
    Attempt multiple selectors with fallback logic supporting ::text and ::attr(...) syntax.

    Args:
        root: BeautifulSoup document or element to query.
        selector_config: Single selector string or a list of selector strings.
        first_only: If True, return only the first extracted value (when available).
        strip: Whether to strip whitespace from extracted text values.

    Returns:
        Dictionary containing:
            - selector: The selector string that produced data (or None)
            - base_selector: The CSS selector used without pseudo suffixes
            - extraction: One of "elements", "text", or "attr"
            - attr_name: Attribute name when extraction is "attr"
            - elements: List of matched elements (may be empty)
            - values: Extracted values (text, attribute values, or elements)
    """
    result: Dict[str, Any] = {
        "selector": None,
        "base_selector": None,
        "extraction": None,
        "attr_name": None,
        "elements": [],
        "values": [],
    }

    if not selector_config:
        return result

    selectors: List[str] = (
        selector_config if isinstance(selector_config, list) else [selector_config]
    )

    for selector in selectors:
        if not selector:
            continue

        extraction_mode = "elements"
        attr_name = None
        base_selector = selector

        if selector.endswith("::text"):
            extraction_mode = "text"
            base_selector = selector[:-6]
        elif "::attr(" in selector:
            extraction_mode = "attr"
            prefix, suffix = selector.split("::attr(", 1)
            base_selector = prefix
            attr_name = suffix.rstrip(")")

        base_selector = base_selector.strip()

        try:
            elements = root.select(base_selector) if base_selector else []
        except Exception:
            logger.debug("Failed to apply selector '%s'", base_selector)
            continue

        if not elements:
            continue

        values: List[Any]
        if extraction_mode == "text":
            values = [
                (elem.get_text(strip=strip) if strip else elem.get_text())
                for elem in elements
                if elem.get_text(strip=True)
            ]
        elif extraction_mode == "attr" and attr_name:
            values = [
                (
                    attr_value.strip()
                    if isinstance(attr_value, str) and strip
                    else attr_value
                )
                for elem in elements
                if (attr_value := elem.get(attr_name))
            ]
        else:
            values = elements

        if not values:
            continue

        if first_only:
            values = values[:1]

        result.update(
            {
                "selector": selector,
                "base_selector": base_selector,
                "extraction": extraction_mode,
                "attr_name": attr_name,
                "elements": elements,
                "values": values,
            }
        )
        return result

    return result


def extract_thumbnail_data_from_element(
    thumbnail_element,
    page_url: str,
    selectors: ThumbnailSelectorConfig,
    base_url: str,
    cleaning_config: Optional[Dict[str, str]] = None,
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

        # Extract title using fallback helper
        title_result = extract_with_selector_fallback(
            thumbnail_element,
            selectors.title,
            first_only=True,
        )
        if title_result["values"]:
            title_value = title_result["values"][0]
            if isinstance(title_value, str):
                data["title"] = title_value.strip()
            elif hasattr(title_value, "get_text"):
                data["title"] = title_value.get_text(strip=True)

        # Extract URL using fallback helper (normalize relative URLs)
        url_result = extract_with_selector_fallback(
            thumbnail_element,
            selectors.url,
            first_only=True,
        )
        if url_result["values"]:
            raw_url = url_result["values"][0]
            href_value = None

            if isinstance(raw_url, str):
                href_value = raw_url.strip()
            elif hasattr(raw_url, "get"):
                candidate_attrs = []
                if url_result["attr_name"]:
                    candidate_attrs.append(url_result["attr_name"])
                candidate_attrs.extend(["href", "data-href", "data-url"])

                for attr_name in candidate_attrs:
                    attr_val = raw_url.get(attr_name)
                    if attr_val:
                        href_value = (
                            attr_val.strip() if isinstance(attr_val, str) else attr_val
                        )
                        break

            if href_value:
                data["url"] = urljoin(base_url, href_value)

        # Extract date if selector is provided
        if selectors.date:
            date_result = extract_with_selector_fallback(
                thumbnail_element,
                selectors.date,
                first_only=True,
            )
            if date_result["values"]:
                date_value = date_result["values"][0]
                if isinstance(date_value, str):
                    data["date"] = date_value.strip()
                elif hasattr(date_value, "get_text"):
                    data["date"] = date_value.get_text(strip=True)
            else:
                logger.warning(
                    f"Date selector '{selectors.date}' failed on page {page_url}"
                )

        # Validate that we have the essential data
        if not data.get("title") and not data.get("url"):
            logger.warning("Thumbnail missing both title and URL")
            return None
        if not data.get("title"):
            logger.warning("Thumbnail missing title")
            return None
        if not data.get("url"):
            logger.warning("Thumbnail missing URL")
            return None

        # Apply cleaning functions if configured
        if cleaning_config:
            data = apply_cleaning(data, cleaning_config, base_url, page_url)

        return data

    except Exception as e:
        logger.error(f"Error extracting thumbnail data: {e}")
        return None


def extract_article_data_from_soup(
    soup,
    article_url: str,
    selectors: ArticleSelectorConfig,
    base_url: str,
    cleaning_config: Optional[Dict[str, str]] = None,
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

        # Extract article body with fallback selector support
        body_result = extract_with_selector_fallback(
            soup,
            selectors.body,
            first_only=False,
        )
        data["body"] = ""
        if body_result["values"]:
            text_values = [
                unicodedata.normalize("NFKD", elem.get_text(separator=" ", strip=True))
                for elem in body_result["values"]
                if elem.get_text(strip=True)
            ]
            data["body"] = " ".join(text_values)
        # Extract article date if selector is provided
        if selectors.date:
            date_result = extract_with_selector_fallback(
                soup,
                selectors.date,
                first_only=True,
            )
            if date_result["values"]:
                date_value = date_result["values"][0]
                if isinstance(date_value, str):
                    data["date"] = date_value.strip()
                elif hasattr(date_value, "get_text"):
                    data["date"] = date_value.get_text(strip=True)
                else:
                    data["date"] = str(date_value).strip()
            else:
                logger.warning(
                    f"Article date selector '{selectors.date}' failed on {article_url}"
                )

        # Extract tags if selector is provided
        data["tags"] = []
        if selectors.tags:
            tags_result = extract_with_selector_fallback(
                soup,
                selectors.tags,
                first_only=False,
            )
            if tags_result["values"]:
                if tags_result["extraction"] in {"text", "attr"}:
                    tags = [
                        str(value).strip()
                        for value in tags_result["values"]
                        if str(value).strip()
                    ]
                else:
                    tags = [
                        elem.get_text(strip=True)
                        for elem in tags_result["values"]
                        if elem.get_text(strip=True)
                    ]
                data["tags"] = tags
            else:
                logger.warning(
                    f"Article tags selector '{selectors.tags}' failed on {article_url}"
                )

        # Apply cleaning functions if configured
        if cleaning_config:
            data = apply_cleaning(data, cleaning_config, base_url, article_url)

        return data

    except Exception as e:
        logger.error(f"Error extracting article data from {article_url}: {e}")
        return {"body": "", "tags": []}
