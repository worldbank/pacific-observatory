"""
Storage pipeline for saving scraped data.

This module provides storage functionality for saving scraped data
in JSONL format with proper organization by country and newspaper.
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Union, Optional
import logging
from ..models import ThumbnailRecord, ArticleRecord

logger = logging.getLogger(__name__)


class JsonlStorage:
    """
    Storage class for saving scraped data in JSONL format.

    Organizes data by country/newspaper structure and maintains
    both raw HTML and processed data.
    """

    def __init__(self, base_data_dir: Union[str, Path] = None):
        """
        Initialize the storage system.

        Args:
            base_data_dir: Base directory for data storage
        """
        if base_data_dir is None:
            # Use environment variable or default
            base_data_dir = os.environ.get("DATA_FOLDER_PATH", "./data/text")

        self.base_data_dir = Path(base_data_dir)
        self.ensure_directories()

    def ensure_directories(self):
        """Ensure the base directory structure exists."""
        # Only create the processed directory - others are created as needed
        processed_dir = self.base_data_dir
        processed_dir.mkdir(parents=True, exist_ok=True)

    def get_newspaper_dir(self, country: str, newspaper: str) -> Path:
        """
        Get the directory path for a specific newspaper.

        Args:
            country: Country code
            newspaper: Newspaper name

        Returns:
            Path to the newspaper's data directory
        """
        # Sanitize names for filesystem
        country = self._sanitize_name(country)
        newspaper = self._sanitize_name(newspaper)

        return self.base_data_dir / country / newspaper

    def _sanitize_name(self, name: str) -> str:
        """
        Sanitize a name for use in filesystem paths.

        Args:
            name: Name to sanitize

        Returns:
            Sanitized name safe for filesystem use
        """
        # Replace spaces with underscores and remove special characters
        import re

        sanitized = re.sub(r"[^\w\-_.]", "_", name.replace(" ", "_").lower())
        return sanitized.strip("_")

    def serialize_for_json(self, obj: Any) -> Any:
        """
        Recursively serialize objects to ensure JSON compatibility.

        Converts HttpUrl objects and other non-serializable types to strings.

        Args:
            obj: Object to serialize

        Returns:
            JSON-serializable version of the object
        """
        # More robust HttpUrl detection
        if hasattr(obj, "__class__"):
            class_name = obj.__class__.__name__
            module_name = getattr(obj.__class__, "__module__", "")
            if (
                "HttpUrl" in class_name
                or "pydantic" in module_name
                and "Url" in class_name
            ):
                return str(obj)

        # Handle Pydantic models by converting to dict first
        if hasattr(obj, "dict") and callable(getattr(obj, "dict")):
            try:
                # This is likely a Pydantic model
                model_dict = obj.dict()
                return self.serialize_for_json(model_dict)
            except:
                # If dict() fails, convert to string
                return str(obj)

        # Handle collections recursively
        if isinstance(obj, dict):
            return {
                key: self.serialize_for_json(value)
                for key, value in obj.items()
            }
        elif isinstance(obj, list):
            return [self.serialize_for_json(item) for item in obj]
        elif isinstance(obj, tuple):
            return tuple(self.serialize_for_json(item) for item in obj)
        else:
            # For any other object that might not be JSON serializable, try to convert to string
            try:
                json.dumps(obj)
                return obj  # It's already JSON serializable
            except (TypeError, ValueError):
                return str(obj)  # Convert non-serializable objects to string

    def save_articles(
        self,
        articles: List[ArticleRecord],
        country: str,
        newspaper: str,
        timestamp: datetime = None,
    ) -> Path:
        """
        Save article records to JSONL file.

        Args:
            articles: List of ArticleRecord objects
            country: Country code
            newspaper: Newspaper name
            timestamp: Optional timestamp for filename

        Returns:
            Path to the saved file
        """
        if timestamp is None:
            timestamp = datetime.now()

        # Create directory
        newspaper_dir = self.get_newspaper_dir(country, newspaper)
        newspaper_dir.mkdir(parents=True, exist_ok=True)

        # Create filename - articles are saved as news.jsonl
        filename = "news.jsonl"
        file_path = newspaper_dir / filename

        # Save data
        with open(file_path, "w", encoding="utf-8") as f:
            for article in articles:
                # Convert to dict and add metadata
                data = article.dict()
                data["_scraped_at"] = timestamp.isoformat()

                # Serialize to handle HttpUrl objects
                serialized_data = self.serialize_for_json(data)

                f.write(json.dumps(serialized_data, ensure_ascii=False) + "\n")

        logger.info(f"Saved {len(articles)} articles to {file_path}")
        return file_path

    def save_metadata(
        self,
        results: Dict[str, Any],
        country: str,
        newspaper: str,
        timestamp: datetime = None,
        metadata_type: str = "news",
    ) -> Path:
        """
        Save scraping metadata and statistics.

        Args:
            results: Scraping results dictionary
            country: Country code
            newspaper: Newspaper name
            timestamp: Optional timestamp for filename
            metadata_type: Type of metadata ("urls" or "news")

        Returns:
            Path to the saved metadata file
        """
        if timestamp is None:
            timestamp = datetime.now()

        # Create metadata directory
        newspaper_dir = self.get_newspaper_dir(country, newspaper)
        metadata_dir = newspaper_dir / "metadata"
        metadata_dir.mkdir(parents=True, exist_ok=True)

        # Create filename based on metadata type
        filename = f"{metadata_type}_metadata_{timestamp.strftime('%Y%m%d_%H%M%S')}.json"
        file_path = metadata_dir / filename

        # Prepare metadata
        metadata = {
            "newspaper": newspaper,
            "country": country,
            "scraped_at": timestamp.isoformat(),
            "success": results.get("success", False),
            "statistics": results.get("statistics", {}),
            "errors": results.get("errors", []),
            "config_info": {
                "config_path": results.get("_config_path"),
                "client_type": results.get("client_type"),
            },
        }

        # Serialize metadata to handle HttpUrl objects
        serialized_metadata = self.serialize_for_json(metadata)

        # Save metadata
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(serialized_metadata, f, indent=2, ensure_ascii=False)

        logger.info(f"Saved metadata to {file_path}")
        return file_path

    def save_failed_urls(
        self,
        failed_urls: List[Dict[str, Any]],
        country: str,
        newspaper: str,
        timestamp: datetime = None,
    ) -> Optional[Path]:
        """
        Save failed URLs to JSONL file in failed subdirectory.

        Args:
            failed_urls: List of failed URL dictionaries with url and status_code
            country: Country code
            newspaper: Newspaper name
            timestamp: Optional timestamp for filename

        Returns:
            Path to the saved file, or None if no failed URLs
        """
        if not failed_urls:
            return None

        if timestamp is None:
            timestamp = datetime.now()

        # Create directory
        newspaper_dir = self.get_newspaper_dir(country, newspaper)
        failed_dir = newspaper_dir / "failed"
        failed_dir.mkdir(parents=True, exist_ok=True)

        # Create filename with timestamp
        filename = f"failed_urls_{timestamp.strftime('%Y%m%d')}.jsonl"
        file_path = failed_dir / filename

        # Serialize failed URLs to handle HttpUrl objects
        serialized_failed_urls = self.serialize_for_json(failed_urls)

        # Save data
        with open(file_path, "w", encoding="utf-8") as f:
            for failed_url in serialized_failed_urls:
                f.write(json.dumps(failed_url, ensure_ascii=False) + "\n")

        logger.info(f"Saved {len(failed_urls)} failed URLs to {file_path}")
        return file_path

    def save_failed_news(
        self,
        failed_news: List[Dict[str, Any]],
        country: str,
        newspaper: str,
        timestamp: datetime = None,
    ) -> Optional[Path]:
        """
        Save failed news articles to JSONL file in failed subdirectory.

        Args:
            failed_news: List of failed news dictionaries with url and status_code
            country: Country code
            newspaper: Newspaper name
            timestamp: Optional timestamp for filename

        Returns:
            Path to the saved file, or None if no failed news
        """
        if not failed_news:
            return None

        if timestamp is None:
            timestamp = datetime.now()

        # Create directory
        newspaper_dir = self.get_newspaper_dir(country, newspaper)
        failed_dir = newspaper_dir / "failed"
        failed_dir.mkdir(parents=True, exist_ok=True)

        # Create filename with timestamp
        filename = f"failed_news_{timestamp.strftime('%Y%m%d')}.jsonl"
        file_path = failed_dir / filename

        # Serialize failed news to handle HttpUrl objects
        serialized_failed_news = self.serialize_for_json(failed_news)

        # Save data
        with open(file_path, "w", encoding="utf-8") as f:
            for failed_article in serialized_failed_news:
                f.write(json.dumps(failed_article, ensure_ascii=False) + "\n")

        logger.info(
            f"Saved {len(failed_news)} failed news articles to {file_path}"
        )
        return file_path

    def save_thumbnails_as_urls(
        self,
        thumbnails: List[ThumbnailRecord],
        country: str,
        newspaper: str,
        timestamp: datetime = None,
    ) -> Optional[Path]:
        """
        Save thumbnails to urls.jsonl file.

        Args:
            thumbnails: List of ThumbnailRecord objects
            country: Country code
            newspaper: Newspaper name
            timestamp: Optional timestamp for metadata

        Returns:
            Path to the saved file, or None if no thumbnails
        """
        if not thumbnails:
            return None

        if timestamp is None:
            timestamp = datetime.now()

        # Create directory
        newspaper_dir = self.get_newspaper_dir(country, newspaper)
        newspaper_dir.mkdir(parents=True, exist_ok=True)

        # Save as urls.jsonl (new naming convention)
        filename = "urls.jsonl"
        file_path = newspaper_dir / filename

        # Save thumbnails as JSONL
        with open(file_path, "w", encoding="utf-8") as f:
            for thumbnail in thumbnails:
                thumb_data = {
                    "url": str(thumbnail.url),
                    "title": thumbnail.title,
                    "date": thumbnail.date,
                }
                f.write(json.dumps(thumb_data, ensure_ascii=False) + "\n")

        logger.info(f"Saved {len(thumbnails)} thumbnails to {file_path}")
        return file_path

    def load_thumbnails_from_urls_file(
        self, country: str, newspaper: str, date: datetime = None
    ) -> Optional[List[ThumbnailRecord]]:
        """
        Load thumbnails from a 'urls_' JSONL file.

        Args:
            country: Country code
            newspaper: Newspaper name
            date: Optional date to load (defaults to today)

        Returns:
            List of ThumbnailRecord objects if file exists, None otherwise
        """
        if date is None:
            date = datetime.now()

        # Get newspaper directory
        newspaper_dir = self.get_newspaper_dir(country, newspaper)

        # Check for urls.jsonl file (new naming convention)
        filename = "urls.jsonl"
        file_path = newspaper_dir / filename

        if not file_path.exists():
            logger.info(f"No existing thumbnails file found: {file_path}")
            return None

        try:
            thumbnails = []
            with open(file_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line:  # Skip empty lines
                        data = json.loads(line)
                        thumbnail = ThumbnailRecord(
                            url=data["url"],
                            title=data["title"],
                            date=data["date"],
                        )
                        thumbnails.append(thumbnail)

            logger.info(
                f"Loaded {len(thumbnails)} existing thumbnails from {file_path}"
            )
            return thumbnails

        except Exception as e:
            logger.error(
                f"Failed to load existing thumbnails from {file_path}: {e}"
            )
            return None

    def load_existing_articles(
        self, country: str, newspaper: str
    ) -> Optional[List[ArticleRecord]]:
        """
        Load existing articles from news.jsonl file.

        Args:
            country: Country code
            newspaper: Newspaper name

        Returns:
            List of ArticleRecord objects if file exists, None otherwise
        """
        # Get newspaper directory
        newspaper_dir = self.get_newspaper_dir(country, newspaper)

        # Check for news.jsonl file
        filename = "news.jsonl"
        file_path = newspaper_dir / filename

        if not file_path.exists():
            logger.info(f"No existing articles file found: {file_path}")
            return None

        try:
            articles = []
            with open(file_path, "r", encoding="utf-8") as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if line:  # Skip empty lines
                        try:
                            data = json.loads(line)
                            # Remove metadata fields that aren't part of ArticleRecord
                            article_data = {
                                k: v
                                for k, v in data.items()
                                if not k.startswith("_")
                            }
                            article = ArticleRecord(**article_data)
                            articles.append(article)
                        except Exception as line_error:
                            logger.warning(
                                f"Failed to parse article on line {line_num} in {file_path}: {line_error}"
                            )
                            continue

            logger.info(
                f"Loaded {len(articles)} existing articles from {file_path}"
            )
            return articles

        except Exception as e:
            logger.error(
                f"Failed to load existing articles from {file_path}: {e}"
            )
            return None

    def get_existing_article_urls(self, country: str, newspaper: str) -> set:
        """
        Get a set of URLs from existing articles for quick lookup.

        Args:
            country: Country code
            newspaper: Newspaper name

        Returns:
            Set of article URLs that already exist
        """
        existing_articles = self.load_existing_articles(country, newspaper)
        if not existing_articles:
            return set()

        # Convert URLs to strings for comparison
        existing_urls = {str(article.url) for article in existing_articles}
        logger.info(
            f"Found {len(existing_urls)} existing article URLs for {newspaper}"
        )
        return existing_urls
