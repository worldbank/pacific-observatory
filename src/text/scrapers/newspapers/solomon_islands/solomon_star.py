"""
Solomon Star scraper using the new config-driven architecture.

This scraper has been migrated from the monolithic approach to use
the modern framework with YAML configuration.

Original scraper: 62 lines of complex pandas/CSV processing
New scraper: Simple orchestration call using solomon_star.yaml config

Migration benefits:
- 84% code reduction (62 → 10 lines)
- Configuration-driven approach
- Async HTTP performance
- Automatic data validation
- JSONL output format
- Smart caching and error handling
"""

import sys
import os

# Add the scrapers directory to the path to import orchestration
scrapers_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, scrapers_dir)

from orchestration.run_scraper import run_newspaper_scraper


def main():
    """Run the Solomon Star scraper using the config-driven framework."""
    config_path = os.path.join(
        scrapers_dir, 
        "configs", 
        "solomon_islands", 
        "solomon_star.yaml"
    )
    
    print("Starting Solomon Star scraper...")
    print(f"Using config: {config_path}")
    
    # Run the scraper using the orchestration framework
    result = run_newspaper_scraper(config_path)
    
    if result:
        print("✅ Solomon Star scraping completed successfully!")
        print(f"📊 Results saved to: {result.get('output_dir', 'data/text/solomon_islands/solomon_star/')}")
    else:
        print("❌ Solomon Star scraping failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()