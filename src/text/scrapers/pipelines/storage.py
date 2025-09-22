"""
Storage pipeline for saving scraped data.

This module provides storage functionality for saving scraped data
in JSONL format with proper organization by country and newspaper.
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Union
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
            base_data_dir = os.environ.get("DATA_FOLDER_PATH", "./data")
        
        self.base_data_dir = Path(base_data_dir)
        self.ensure_directories()
    
    def ensure_directories(self):
        """Ensure the base directory structure exists."""
        directories = [
            self.base_data_dir / "raw",
            self.base_data_dir / "processed",
            self.base_data_dir / "logs",
            self.base_data_dir / "failed"
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
    
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
        
        return self.base_data_dir / "processed" / country / newspaper
    
    def get_raw_dir(self, country: str, newspaper: str) -> Path:
        """
        Get the raw data directory path for a specific newspaper.
        
        Args:
            country: Country code
            newspaper: Newspaper name
            
        Returns:
            Path to the newspaper's raw data directory
        """
        country = self._sanitize_name(country)
        newspaper = self._sanitize_name(newspaper)
        
        return self.base_data_dir / "raw" / country / newspaper
    
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
        sanitized = re.sub(r'[^\w\-_.]', '_', name.lower())
        return sanitized.strip('_')
    
    def save_thumbnails(
        self,
        thumbnails: List[ThumbnailRecord],
        country: str,
        newspaper: str,
        timestamp: datetime = None
    ) -> Path:
        """
        Save thumbnail records to JSONL file.
        
        Args:
            thumbnails: List of ThumbnailRecord objects
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
        
        # Create filename with timestamp
        filename = f"thumbnails_{timestamp.strftime('%Y%m%d_%H%M%S')}.jsonl"
        file_path = newspaper_dir / filename
        
        # Save data
        with open(file_path, 'w', encoding='utf-8') as f:
            for thumbnail in thumbnails:
                # Convert to dict and add metadata
                data = thumbnail.dict()
                data['_scraped_at'] = timestamp.isoformat()
                data['_country'] = country
                data['_newspaper'] = newspaper
                
                f.write(json.dumps(data, ensure_ascii=False) + '\n')
        
        logger.info(f"Saved {len(thumbnails)} thumbnails to {file_path}")
        return file_path
    
    def save_articles(
        self,
        articles: List[ArticleRecord],
        country: str,
        newspaper: str,
        timestamp: datetime = None
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
        
        # Create filename with timestamp
        filename = f"articles_{timestamp.strftime('%Y%m%d_%H%M%S')}.jsonl"
        file_path = newspaper_dir / filename
        
        # Save data
        with open(file_path, 'w', encoding='utf-8') as f:
            for article in articles:
                # Convert to dict and add metadata
                data = article.dict()
                data['_scraped_at'] = timestamp.isoformat()
                
                f.write(json.dumps(data, ensure_ascii=False) + '\n')
        
        logger.info(f"Saved {len(articles)} articles to {file_path}")
        return file_path
    
    def _save_thumbnails_dict(
        self,
        thumbnails_data: List[Dict[str, Any]],
        country: str,
        newspaper: str,
        timestamp: datetime = None
    ) -> Path:
        """
        Save thumbnail data directly from dictionary format.
        
        Args:
            thumbnails_data: List of thumbnail dictionaries (already JSON-serializable)
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
        
        # Create filename with timestamp
        filename = f"thumbnails_{timestamp.strftime('%Y%m%d_%H%M%S')}.jsonl"
        file_path = newspaper_dir / filename
        
        # Save data
        with open(file_path, 'w', encoding='utf-8') as f:
            for thumbnail_data in thumbnails_data:
                # Add metadata
                data = thumbnail_data.copy()
                data['_scraped_at'] = timestamp.isoformat()
                data['_country'] = country
                data['_newspaper'] = newspaper
                
                f.write(json.dumps(data, ensure_ascii=False) + '\n')
        
        logger.info(f"Saved {len(thumbnails_data)} thumbnails to {file_path}")
        return file_path
    
    def _save_articles_dict(
        self,
        articles_data: List[Dict[str, Any]],
        country: str,
        newspaper: str,
        timestamp: datetime = None
    ) -> Path:
        """
        Save article data directly from dictionary format.
        
        Args:
            articles_data: List of article dictionaries (already JSON-serializable)
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
        
        # Create filename with timestamp
        filename = f"articles_{timestamp.strftime('%Y%m%d_%H%M%S')}.jsonl"
        file_path = newspaper_dir / filename
        
        # Save data
        with open(file_path, 'w', encoding='utf-8') as f:
            for article_data in articles_data:
                # Add metadata
                data = article_data.copy()
                data['_scraped_at'] = timestamp.isoformat()
                
                f.write(json.dumps(data, ensure_ascii=False) + '\n')
        
        logger.info(f"Saved {len(articles_data)} articles to {file_path}")
        return file_path
    
    def save_raw_html(
        self,
        url: str,
        html_content: str,
        country: str,
        newspaper: str,
        timestamp: datetime = None
    ) -> Path:
        """
        Save raw HTML content for reproducibility.
        
        Args:
            url: URL of the scraped page
            html_content: Raw HTML content
            country: Country code
            newspaper: Newspaper name
            timestamp: Optional timestamp for filename
            
        Returns:
            Path to the saved file
        """
        if timestamp is None:
            timestamp = datetime.now()
        
        # Create directory
        raw_dir = self.get_raw_dir(country, newspaper)
        raw_dir.mkdir(parents=True, exist_ok=True)
        
        # Create filename from URL and timestamp
        from urllib.parse import urlparse
        parsed_url = urlparse(url)
        url_part = self._sanitize_name(parsed_url.path.strip('/').replace('/', '_'))
        if not url_part:
            url_part = 'index'
        
        filename = f"{url_part}_{timestamp.strftime('%Y%m%d_%H%M%S')}.html"
        file_path = raw_dir / filename
        
        # Save HTML content
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        logger.debug(f"Saved raw HTML for {url} to {file_path}")
        return file_path
    
    def save_scraping_results(
        self,
        results: Dict[str, Any],
        country: str,
        newspaper: str,
        timestamp: datetime = None
    ) -> Dict[str, Path]:
        """
        Save complete scraping results including metadata.
        
        Args:
            results: Scraping results dictionary
            country: Country code
            newspaper: Newspaper name
            timestamp: Optional timestamp for filename
            
        Returns:
            Dictionary mapping data types to saved file paths
        """
        if timestamp is None:
            timestamp = datetime.now()
        
        saved_files = {}
        
        # Save thumbnails if present
        if 'thumbnails' in results.get('data', {}):
            thumbnails_data = results['data']['thumbnails']
            if thumbnails_data:
                # Save thumbnails directly as dict data (already JSON-serializable)
                saved_files['thumbnails'] = self._save_thumbnails_dict(thumbnails_data, country, newspaper, timestamp)
        
        # Save articles if present
        if 'articles' in results.get('data', {}):
            articles_data = results['data']['articles']
            if articles_data:
                # Save articles directly as dict data (already JSON-serializable)
                saved_files['articles'] = self._save_articles_dict(articles_data, country, newspaper, timestamp)
        
        # Save metadata and statistics
        metadata_file = self.save_metadata(results, country, newspaper, timestamp)
        saved_files['metadata'] = metadata_file
        
        return saved_files
    
    def save_metadata(
        self,
        results: Dict[str, Any],
        country: str,
        newspaper: str,
        timestamp: datetime = None
    ) -> Path:
        """
        Save scraping metadata and statistics.
        
        Args:
            results: Scraping results dictionary
            country: Country code
            newspaper: Newspaper name
            timestamp: Optional timestamp for filename
            
        Returns:
            Path to the saved metadata file
        """
        if timestamp is None:
            timestamp = datetime.now()
        
        # Create directory
        newspaper_dir = self.get_newspaper_dir(country, newspaper)
        newspaper_dir.mkdir(parents=True, exist_ok=True)
        
        # Create filename
        filename = f"metadata_{timestamp.strftime('%Y%m%d_%H%M%S')}.json"
        file_path = newspaper_dir / filename
        
        # Prepare metadata
        metadata = {
            'newspaper': newspaper,
            'country': country,
            'scraped_at': timestamp.isoformat(),
            'success': results.get('success', False),
            'statistics': results.get('statistics', {}),
            'errors': results.get('errors', []),
            'config_info': {
                'config_path': results.get('_config_path'),
                'client_type': results.get('client_type')
            }
        }
        
        # Save metadata
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Saved metadata to {file_path}")
        return file_path
    
    def load_latest_articles(self, country: str, newspaper: str) -> List[ArticleRecord]:
        """
        Load the most recent articles for a newspaper.
        
        Args:
            country: Country code
            newspaper: Newspaper name
            
        Returns:
            List of ArticleRecord objects
        """
        newspaper_dir = self.get_newspaper_dir(country, newspaper)
        
        # Find the most recent articles file
        article_files = list(newspaper_dir.glob("articles_*.jsonl"))
        if not article_files:
            return []
        
        # Sort by filename (which includes timestamp)
        latest_file = sorted(article_files)[-1]
        
        # Load articles
        articles = []
        with open(latest_file, 'r', encoding='utf-8') as f:
            for line in f:
                data = json.loads(line)
                # Remove metadata fields before creating ArticleRecord
                data.pop('_scraped_at', None)
                articles.append(ArticleRecord(**data))
        
        logger.info(f"Loaded {len(articles)} articles from {latest_file}")
        return articles
    
    def get_storage_stats(self, country: str = None, newspaper: str = None) -> Dict[str, Any]:
        """
        Get storage statistics for the specified scope.
        
        Args:
            country: Optional country filter
            newspaper: Optional newspaper filter
            
        Returns:
            Dictionary with storage statistics
        """
        stats = {
            'total_newspapers': 0,
            'total_articles': 0,
            'total_thumbnails': 0,
            'countries': {},
            'newspapers': {}
        }
        
        processed_dir = self.base_data_dir / "processed"
        
        if not processed_dir.exists():
            return stats
        
        # Iterate through countries
        for country_dir in processed_dir.iterdir():
            if not country_dir.is_dir():
                continue
            
            country_name = country_dir.name
            if country and country_name != self._sanitize_name(country):
                continue
            
            stats['countries'][country_name] = {
                'newspapers': 0,
                'articles': 0,
                'thumbnails': 0
            }
            
            # Iterate through newspapers in this country
            for newspaper_dir in country_dir.iterdir():
                if not newspaper_dir.is_dir():
                    continue
                
                newspaper_name = newspaper_dir.name
                if newspaper and newspaper_name != self._sanitize_name(newspaper):
                    continue
                
                stats['total_newspapers'] += 1
                stats['countries'][country_name]['newspapers'] += 1
                
                # Count articles and thumbnails
                article_files = list(newspaper_dir.glob("articles_*.jsonl"))
                thumbnail_files = list(newspaper_dir.glob("thumbnails_*.jsonl"))
                
                newspaper_articles = 0
                newspaper_thumbnails = 0
                
                # Count lines in article files
                for article_file in article_files:
                    with open(article_file, 'r') as f:
                        newspaper_articles += sum(1 for _ in f)
                
                # Count lines in thumbnail files
                for thumbnail_file in thumbnail_files:
                    with open(thumbnail_file, 'r') as f:
                        newspaper_thumbnails += sum(1 for _ in f)
                
                stats['total_articles'] += newspaper_articles
                stats['total_thumbnails'] += newspaper_thumbnails
                stats['countries'][country_name]['articles'] += newspaper_articles
                stats['countries'][country_name]['thumbnails'] += newspaper_thumbnails
                
                stats['newspapers'][f"{country_name}/{newspaper_name}"] = {
                    'articles': newspaper_articles,
                    'thumbnails': newspaper_thumbnails
                }
        
        return stats
