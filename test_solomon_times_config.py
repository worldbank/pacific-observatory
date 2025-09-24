#!/usr/bin/env python3
"""
Test script to validate Solomon Times configuration.
"""

import sys
from pathlib import Path

# Add the src directory to Python path for imports
project_root = Path(__file__).parent
src_dir = project_root / "src"
sys.path.insert(0, str(src_dir))

from text.scrapers.factory import create_scraper_from_file

def test_solomon_times_config():
    """Test loading Solomon Times configuration."""
    config_path = project_root / "src" / "text" / "scrapers" / "configs" / "solomon_islands" / "solomon_times.yaml"
    
    print(f"Testing Solomon Times configuration: {config_path}")
    
    try:
        # Try to create scraper from config
        scraper = create_scraper_from_file(config_path)
        
        print("✅ Configuration loaded successfully!")
        print(f"   Name: {scraper.name}")
        print(f"   Country: {scraper.country}")
        print(f"   Base URL: {scraper.base_url}")
        print(f"   Client: {scraper.client_type}")
        print(f"   Listing Strategy: {type(scraper.listing_strategy).__name__}")
        
        # Test cleaning functions
        from text.scrapers.pipelines.cleaning import get_cleaning_function
        
        date_func = get_cleaning_function("clean_solomon_times_date")
        content_func = get_cleaning_function("clean_solomon_times_content")
        tags_func = get_cleaning_function("clean_solomon_times_tags")
        
        if date_func and content_func and tags_func:
            print("✅ All cleaning functions found!")
            
            # Test date extraction from URL
            test_url = "https://www.solomontimes.com/news/latest/2024/05"
            test_date = date_func("", page_url=test_url)
            print(f"   Date extraction test: '{test_url}' -> '{test_date}'")
            
        else:
            print("❌ Some cleaning functions missing")
            
        return True
        
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_solomon_times_config()
    sys.exit(0 if success else 1)
