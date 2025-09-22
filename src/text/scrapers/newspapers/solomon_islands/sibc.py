#!/usr/bin/env python3
"""
SIBC (Solomon Islands Broadcasting Corporation) Scraper

This script has been migrated to use the new config-driven architecture.
All site-specific details are now in configs/solomon_islands/sibc.yaml
and the scraping logic uses the generic framework.
"""

import asyncio
import sys
from pathlib import Path

# Add the scrapers directory to the path
scrapers_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(scrapers_dir))

from orchestration.run_scraper import run_single_scraper


async def main():
    """
    Main function to run the SIBC scraper using the new architecture.
    
    This now uses the generic orchestration module with the SIBC configuration
    instead of custom scraping logic.
    """
    # Path to the SIBC configuration file
    config_path = scrapers_dir / "configs" / "solomon_islands" / "sibc.yaml"
    
    if not config_path.exists():
        print(f"❌ Configuration file not found: {config_path}")
        print("Please ensure the SIBC configuration file exists.")
        sys.exit(1)
    
    try:
        # Run the scraper using the orchestration module
        results = await run_single_scraper(
            config_path=config_path,
            storage_dir=None,  # Use default storage location
            save_results=True
        )
        
        if results['success']:
            print("✅ SIBC scraping completed successfully!")
            stats = results.get('statistics', {})
            print(f"📊 Articles scraped: {stats.get('articles_scraped', 0)}")
            print(f"📊 Thumbnails found: {stats.get('thumbnails_found', 0)}")
            
            if 'timing' in results:
                duration = results['timing']['duration_seconds']
                print(f"⏱️  Duration: {duration:.1f} seconds")
        else:
            print(f"❌ SIBC scraping failed: {results.get('error', 'Unknown error')}")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ Error running SIBC scraper: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
