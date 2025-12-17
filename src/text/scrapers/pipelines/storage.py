"""
Storage pipeline for saving scraped data.

This module provides storage functionality for saving scraped data
in CSV format with proper organization by country and newspaper.
Metadata and error logs are saved in JSON format.
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Union, Optional
import logging
from ..models import ThumbnailRecord, ArticleRecord

logger = logging.getLogger(__name__)


class CSVStorage:
    """
    Storage class for saving scraped data in CSV format.

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

        # Streaming state tracking
        self._streaming_file_handles: Dict[
            str, Any
        ] = {}  # Track open file handles by newspaper
        self._streaming_headers_written: Dict[
            str, bool
        ] = {}  # Track if headers written

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

    def _get_streaming_key(self, country: str, newspaper: str) -> str:
        """Get a unique key for streaming state tracking."""
        country = self._sanitize_name(country)
        newspaper = self._sanitize_name(newspaper)
        return f"{country}/{newspaper}"

    def initialize_csv(
        self,
        country: str,
        newspaper: str,
        timestamp: datetime = None,
    ) -> Path:
        """
        Initialize CSV file with headers for streaming writes.

        Args:
            country: Country code
            newspaper: Newspaper name
            timestamp: Optional timestamp for metadata

        Returns:
            Path to the initialized CSV file
        """
        import csv

        if timestamp is None:
            timestamp = datetime.now()

        # Create directory
        newspaper_dir = self.get_newspaper_dir(country, newspaper)
        newspaper_dir.mkdir(parents=True, exist_ok=True)

        # Create filename
        filename = "news.csv"
        file_path = newspaper_dir / filename

        # Define CSV headers
        headers = [
            "url",
            "title",
            "date",
            "body",
            "tags",
            "source",
            "country",
            "_scraped_at",
        ]

        # Write headers to file
        with open(file_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()

        logger.info(f"Initialized CSV file: {file_path}")

        # Track that headers have been written
        key = self._get_streaming_key(country, newspaper)
        self._streaming_headers_written[key] = True

        return file_path

    def append_article(
        self,
        article: ArticleRecord,
        country: str,
        newspaper: str,
        timestamp: datetime = None,
    ) -> Path:
        """
        Append a single article to the CSV file (streaming write).

        Args:
            article: ArticleRecord object to append
            country: Country code
            newspaper: Newspaper name
            timestamp: Optional timestamp for metadata

        Returns:
            Path to the CSV file
        """
        import csv

        if timestamp is None:
            timestamp = datetime.now()

        # Get newspaper directory
        newspaper_dir = self.get_newspaper_dir(country, newspaper)
        newspaper_dir.mkdir(parents=True, exist_ok=True)

        # Get file path
        filename = "news.csv"
        file_path = newspaper_dir / filename

        # Define CSV headers in the correct order
        headers = [
            "url",
            "title",
            "date",
            "body",
            "tags",
            "source",
            "country",
            "_scraped_at",
        ]

        # Convert article to dictionary
        article_dict = article.model_dump()

        # Convert tags list to comma-separated string
        if isinstance(article_dict.get("tags"), list):
            article_dict["tags"] = ",".join(article_dict["tags"])

        # Convert HttpUrl to string
        article_dict["url"] = str(article_dict["url"])

        # Add timestamp
        article_dict["_scraped_at"] = timestamp.isoformat()

        # Build row with only the fields in headers, in the correct order
        row = {}
        for header in headers:
            row[header] = article_dict.get(header, "")

        # Append to CSV file
        with open(file_path, "a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(
                f, fieldnames=headers, restval="", extrasaction="ignore"
            )
            writer.writerow(row)

        return file_path

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
            except Exception:
                # If dict() fails, convert to string
                return str(obj)

        # Handle collections recursively
        if isinstance(obj, dict):
            return {key: self.serialize_for_json(value) for key, value in obj.items()}
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
        Save article records to CSV file.

        Args:
            articles: List of ArticleRecord objects
            country: Country code
            newspaper: Newspaper name
            timestamp: Optional timestamp for filename

        Returns:
            Path to the saved file
        """
        import pandas as pd

        if timestamp is None:
            timestamp = datetime.now()

        # Create directory
        newspaper_dir = self.get_newspaper_dir(country, newspaper)
        newspaper_dir.mkdir(parents=True, exist_ok=True)

        # Create filename - articles are saved as news.csv
        filename = "news.csv"
        file_path = newspaper_dir / filename

        # Convert articles to dictionaries
        data = []
        for article in articles:
            article_dict = article.model_dump()
            article_dict["_scraped_at"] = timestamp.isoformat()
            # Convert tags list to comma-separated string
            if isinstance(article_dict.get("tags"), list):
                article_dict["tags"] = ",".join(article_dict["tags"])
            # Convert HttpUrl to string
            article_dict["url"] = str(article_dict["url"])
            data.append(article_dict)

        # Create DataFrame and save to CSV
        df = pd.DataFrame(data)
        df.to_csv(file_path, index=None, encoding="utf-8")

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
        filename = (
            f"{metadata_type}_metadata_{timestamp.strftime('%Y%m%d_%H%M%S')}.json"
        )
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
        Save failed URLs to CSV file in failed subdirectory.

        Args:
            failed_urls: List of failed URL dictionaries with url and status_code
            country: Country code
            newspaper: Newspaper name
            timestamp: Optional timestamp for filename

        Returns:
            Path to the saved file, or None if no failed URLs
        """
        import pandas as pd

        if not failed_urls:
            return None

        if timestamp is None:
            timestamp = datetime.now()

        # Create directory
        newspaper_dir = self.get_newspaper_dir(country, newspaper)
        failed_dir = newspaper_dir / "failed"
        failed_dir.mkdir(parents=True, exist_ok=True)

        # Create filename with timestamp
        filename = f"failed_urls_{timestamp.strftime('%Y%m%d')}.csv"
        file_path = failed_dir / filename

        # Convert to DataFrame and save to CSV
        df = pd.DataFrame(failed_urls)
        # Convert any HttpUrl objects to strings
        for col in df.columns:
            if df[col].dtype == "object":
                df[col] = df[col].apply(
                    lambda x: (
                        str(x)
                        if hasattr(x, "__class__") and "HttpUrl" in x.__class__.__name__
                        else x
                    )
                )

        df.to_csv(file_path, index=False, encoding="utf-8")

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
        Save failed news articles to CSV file in failed subdirectory.

        Args:
            failed_news: List of failed news dictionaries with url and status_code
            country: Country code
            newspaper: Newspaper name
            timestamp: Optional timestamp for filename

        Returns:
            Path to the saved file, or None if no failed news
        """
        import pandas as pd

        if not failed_news:
            return None

        if timestamp is None:
            timestamp = datetime.now()

        # Create directory
        newspaper_dir = self.get_newspaper_dir(country, newspaper)
        failed_dir = newspaper_dir / "failed"
        failed_dir.mkdir(parents=True, exist_ok=True)

        # Create filename with timestamp
        filename = f"failed_news_{timestamp.strftime('%Y%m%d')}.csv"
        file_path = failed_dir / filename

        # Convert to DataFrame and save to CSV
        df = pd.DataFrame(failed_news)
        # Convert any HttpUrl objects to strings
        for col in df.columns:
            if df[col].dtype == "object":
                df[col] = df[col].apply(
                    lambda x: (
                        str(x)
                        if hasattr(x, "__class__") and "HttpUrl" in x.__class__.__name__
                        else x
                    )
                )

        df.to_csv(file_path, index=False, encoding="utf-8")

        logger.info(f"Saved {len(failed_news)} failed news articles to {file_path}")
        return file_path

    def save_thumbnails_as_urls(
        self,
        thumbnails: List[ThumbnailRecord],
        country: str,
        newspaper: str,
        timestamp: datetime = None,
    ) -> Optional[Path]:
        """
        Save thumbnails to urls.csv file.

        Args:
            thumbnails: List of ThumbnailRecord objects
            country: Country code
            newspaper: Newspaper name
            timestamp: Optional timestamp for metadata

        Returns:
            Path to the saved file, or None if no thumbnails
        """
        import pandas as pd

        if not thumbnails:
            return None

        if timestamp is None:
            timestamp = datetime.now()

        # Create directory
        newspaper_dir = self.get_newspaper_dir(country, newspaper)
        newspaper_dir.mkdir(parents=True, exist_ok=True)

        # Save as urls.csv
        filename = "urls.csv"
        file_path = newspaper_dir / filename

        # Convert thumbnails to dictionaries
        data = []
        for thumbnail in thumbnails:
            thumb_data = {
                "url": str(thumbnail.url),
                "title": thumbnail.title,
                "date": thumbnail.date,
            }
            data.append(thumb_data)

        # Create DataFrame and save to CSV
        df = pd.DataFrame(data)
        df.to_csv(file_path, index=False, encoding="utf-8")

        logger.info(f"Saved {len(thumbnails)} thumbnails to {file_path}")
        return file_path

    def load_existing_articles(
        self, country: str, newspaper: str
    ) -> Optional[List[ArticleRecord]]:
        """
        Load existing articles from news.csv file.

        Args:
            country: Country code
            newspaper: Newspaper name

        Returns:
            List of ArticleRecord objects if file exists, None otherwise
        """
        import pandas as pd

        # Get newspaper directory
        newspaper_dir = self.get_newspaper_dir(country, newspaper)

        # Check for news.csv file
        filename = "news.csv"
        file_path = newspaper_dir / filename

        if not file_path.exists():
            logger.info(f"No existing articles file found: {file_path}")
            return None

        try:
            # Read CSV file
            df = pd.read_csv(file_path, encoding="utf-8")
            articles = []

            for _, row in df.iterrows():
                try:
                    # Convert row to dictionary
                    article_data = row.to_dict()

                    # Remove metadata fields that aren't part of ArticleRecord
                    article_data = {
                        k: v for k, v in article_data.items() if not k.startswith("_")
                    }

                    # Handle NaN values
                    article_data = {
                        k: v if pd.notna(v) else None for k, v in article_data.items()
                    }

                    # Parse tags from comma-separated string back to list
                    if "tags" in article_data and isinstance(article_data["tags"], str):
                        article_data["tags"] = [
                            tag.strip()
                            for tag in article_data["tags"].split(",")
                            if tag.strip()
                        ]

                    article = ArticleRecord(**article_data)
                    articles.append(article)
                except Exception as row_error:
                    logger.warning(
                        f"Failed to parse article row in {file_path}: {row_error}"
                    )
                    continue

            logger.info(f"Loaded {len(articles)} existing articles from {file_path}")
            return articles

        except Exception as e:
            logger.error(f"Failed to load existing articles from {file_path}: {e}")
            return None

    def get_existing_article_urls(self, country: str, newspaper: str) -> set:
        """
        Get set of existing article URLs from news.csv file.

        Args:
            country: Country code
            newspaper: Newspaper name

        Returns:
            Set of existing article URLs
        """
        import pandas as pd

        # Get newspaper directory
        newspaper_dir = self.get_newspaper_dir(country, newspaper)

        # Check for news.csv file
        filename = "news.csv"
        file_path = newspaper_dir / filename

        if not file_path.exists():
            logger.info(f"No existing articles file found: {file_path}")
            return set()

        try:
            # Read CSV file and extract URLs
            df = pd.read_csv(file_path, encoding="utf-8")
            urls = set(df["url"].astype(str).unique())
            logger.info(f"Found {len(urls)} existing article URLs")
            return urls

        except Exception as e:
            logger.error(f"Failed to get existing article URLs from {file_path}: {e}")
            return set()

    def load_urls_from_csv(
        self, country: str, newspaper: str
    ) -> Optional[List[ThumbnailRecord]]:
        """
        Load thumbnail URLs from urls.csv file.

        Args:
            country: Country code
            newspaper: Newspaper name

        Returns:
            List of ThumbnailRecord objects if file exists, None otherwise
        """
        import pandas as pd

        # Get newspaper directory
        newspaper_dir = self.get_newspaper_dir(country, newspaper)

        # Check for urls.csv file
        filename = "urls.csv"
        file_path = newspaper_dir / filename

        if not file_path.exists():
            logger.warning(f"No URLs file found: {file_path}")
            return None

        try:
            # Read CSV file
            df = pd.read_csv(file_path, encoding="utf-8")
            thumbnails = []

            for _, row in df.iterrows():
                try:
                    # Convert row to dictionary
                    thumb_data = row.to_dict()

                    # Handle NaN values
                    thumb_data = {
                        k: v if pd.notna(v) else None for k, v in thumb_data.items()
                    }

                    thumbnail = ThumbnailRecord(**thumb_data)
                    thumbnails.append(thumbnail)
                except Exception as row_error:
                    logger.warning(
                        f"Failed to parse thumbnail row in {file_path}: {row_error}"
                    )
                    continue

            logger.info(f"Loaded {len(thumbnails)} thumbnails from {file_path}")
            return thumbnails

        except Exception as e:
            logger.error(f"Failed to load URLs from {file_path}: {e}")
            return None
