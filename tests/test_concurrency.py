#!/usr/bin/env python3
"""
Test script to verify concurrency parameter implementation.
"""

import asyncio
import yaml
from pathlib import Path
from src.text.scrapers.newspaper_scraper import NewspaperScraper

async def test_sibc_concurrency():
    """Test SIBC scraper with concurrency parameter."""
    
    # Load SIBC config
    config_path = Path("src/text/scrapers/configs/solomon_islands/sibc.yaml")
    
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    print(f"Loaded config for {config['name']}")
    print(f"Concurrency setting: {config.get('concurrency', 'Not set')}")
    
    # Create scraper instance
    scraper = NewspaperScraper(config)
    
    # Get HTTP client and check its concurrency setting
    http_client = scraper._get_http_client()
    print(f"HTTP client max_concurrent: {http_client.max_concurrent}")
    print(f"HTTP client semaphore value: {http_client._semaphore._value}")
    
    # Test that the semaphore is properly configured
    assert http_client.max_concurrent == config['concurrency'], \
        f"Expected {config['concurrency']}, got {http_client.max_concurrent}"
    
    assert http_client._semaphore._value == config['concurrency'], \
        f"Semaphore value should be {config['concurrency']}, got {http_client._semaphore._value}"
    
    print("✅ Concurrency parameter is correctly configured!")
    
    # Test a small scraping operation to verify it works
    try:
        print("\nTesting small scraping operation...")
        
        # Discover just a few listing URLs for testing
        listing_urls = await scraper.discover_listing_urls()
        print(f"Discovered {len(listing_urls)} listing URLs")
        
        if listing_urls:
            # Test scraping just the first few URLs
            test_urls = listing_urls[:3]  # Only test first 3 URLs
            thumbnails = await scraper.scrape_thumbnails(test_urls)
            print(f"Successfully scraped {len(thumbnails)} thumbnails")
            
            if thumbnails:
                print("Sample thumbnail:")
                print(f"  Title: {thumbnails[0].title}")
                print(f"  URL: {thumbnails[0].url}")
                print(f"  Date: {thumbnails[0].date}")
        
        print("✅ Scraping test completed successfully!")
        
    except Exception as e:
        print(f"⚠️  Scraping test failed (this might be expected): {e}")
    
    finally:
        # Cleanup
        scraper.cleanup()

if __name__ == "__main__":
    asyncio.run(test_sibc_concurrency())
