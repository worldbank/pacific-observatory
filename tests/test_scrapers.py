"""Integration tests for newspaper scrapers.

Each test exercises a scraper with a modified configuration to limit
the scope to 3 pages and 3 articles. Results are written under ``tests/data``.
"""

import asyncio
import yaml
from pathlib import Path
import pytest

# Add project root to path to allow absolute imports
import sys
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / 'src'))

from text.scrapers.newspaper_scraper import NewspaperScraper

CONFIGS_DIR = PROJECT_ROOT / "src" / "text" / "scrapers" / "configs"
DATA_DIR = Path(__file__).parent / "data"

# Ensure the data directory exists for storing test artifacts.
DATA_DIR.mkdir(parents=True, exist_ok=True)


@pytest.mark.parametrize(
    "config_path",
    [
        cfg
        for cfg in CONFIGS_DIR.rglob("*.yaml")
        if cfg.name != "template.yaml"
    ],
    ids=lambda cfg: cfg.stem,
)
@pytest.mark.asyncio
async def test_scraper_config(config_path: Path) -> None:
    """Run a scraper with a modified config to limit pages and articles."""
    
    # Load the original YAML config
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)

    # Modify the config for testing
    config['max_pages'] = 3
    config['max_articles'] = 3

    # Instantiate the scraper with the modified config
    scraper = NewspaperScraper(config)

    # Override the storage path to use the test data directory
    scraper._storage.storage_dir = DATA_DIR

    # Run the scraper
    results = await scraper.run_full_scrape()

    # Assert that the scraping was successful
    assert results['success'], f"Scraper run failed for {config_path.name}"

    # Optional: Add more specific assertions here, e.g., check stats
    stats = results.get('statistics', {})
    assert stats.get('thumbnails_found', 0) > 0, "No thumbnails were found."
    assert stats.get('articles_scraped', 0) > 0, "No articles were scraped."
    assert stats.get('articles_scraped', 0) <= 3, "Scraped more articles than the limit."
