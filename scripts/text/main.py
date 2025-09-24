#!/usr/bin/env python3
"""
Pacific Observatory - Text Scraping Main Entry Point

This script provides a unified interface for running newspaper scrapers
using the new config-driven architecture.

Usage:
    python scripts/text/main.py --help
    python scripts/text/main.py sibc
    python scripts/text/main.py --list-scrapers
    python scripts/text/main.py --list-countries
"""

import asyncio
import argparse
import os
import sys
from pathlib import Path
import logging
from datetime import datetime
from typing import Optional

# Set up the data folder path
os.environ["DATA_FOLDER_PATH"] = "data/text"

# Add the src directory to Python path for imports
project_root = Path(__file__).parent.parent.parent
src_dir = project_root / "src"
sys.path.insert(0, str(src_dir))

# Import the orchestration module directly without using the orchestration script
# We'll implement the scraper running logic here to avoid import issues
import asyncio
import logging
from text.scrapers.factory import create_scraper_from_file, find_config_files
from text.scrapers.pipelines.storage import JsonlStorage


def setup_logging(level: str = "INFO", log_file: Optional[Path] = None):
    """
    Set up logging configuration.
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR)
        log_file: Optional log file path
    """
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    handlers = [logging.StreamHandler(sys.stdout)]
    
    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        handlers.append(logging.FileHandler(log_file))
    
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format=log_format,
        handlers=handlers
    )


async def run_single_scraper(
    config_path: Path,
    storage_dir: Optional[Path] = None,
    save_results: bool = True,
    update_mode: bool = False
) -> dict:
    """
    Run a single newspaper scraper.
    
    Args:
        config_path: Path to the newspaper configuration file
        storage_dir: Optional custom storage directory
        save_results: Whether to save results to disk
        update_mode: Whether to run in update mode (skip existing articles)
        
    Returns:
        Dictionary with scraping results
    """
    logger = logging.getLogger(__name__)
    
    try:
        # Create scraper from config file
        logger.info(f"Loading scraper configuration from: {config_path}")
        scraper = create_scraper_from_file(config_path)
        
        # Initialize storage if needed
        storage = None
        if save_results:
            storage = JsonlStorage(storage_dir)
        
        # Run the scraping operation
        if update_mode:
            logger.info(f"Starting UPDATE scrape for {scraper.name} ({scraper.country})")
        else:
            logger.info(f"Starting FULL scrape for {scraper.name} ({scraper.country})")
        start_time = datetime.now()
        
        if update_mode:
            results = await scraper.run_update_scrape()
        else:
            results = await scraper.run_full_scrape()
        
        end_time = datetime.now()
        duration = end_time - start_time
        
        # Add timing information
        results['timing'] = {
            'start_time': start_time.isoformat(),
            'end_time': end_time.isoformat(),
            'duration_seconds': duration.total_seconds()
        }
        
        # Results are already saved by the scraper itself
        # Just get the file paths from the scraper
        if save_results and results['success']:
            saved_files = getattr(scraper, '_saved_files', {})
            results['saved_files'] = {str(k): str(v) for k, v in saved_files.items()}
        
        # Clean up resources
        scraper.cleanup()
        
        # Log summary
        if results['success']:
            stats = results['statistics']
            logger.info(
                f"Scraping completed successfully in {duration.total_seconds():.1f}s: "
                f"{stats['articles_scraped']} articles from {stats['thumbnails_found']} thumbnails"
            )
        else:
            logger.error(f"Scraping failed: {results.get('error', 'Unknown error')}")
        
        return results
        
    except Exception as e:
        logger.error(f"Error running scraper: {e}")
        return {
            'success': False,
            'error': str(e),
            'newspaper': getattr(scraper, 'name', 'Unknown') if 'scraper' in locals() else 'Unknown',
            'country': getattr(scraper, 'country', 'Unknown') if 'scraper' in locals() else 'Unknown'
        }


def get_scrapers_dir():
    """Get the scrapers directory path."""
    return project_root / "src" / "text" / "scrapers"


def get_default_configs_dir():
    """Get the default configs directory path."""
    return get_scrapers_dir() / "configs"


def list_available_scrapers():
    """List all available newspaper scrapers."""
    scrapers_dir = get_scrapers_dir()
    configs_dir = scrapers_dir / "configs"
    
    if not configs_dir.exists():
        print("❌ No scrapers directory found")
        return
    
    print("📰 Available Newspaper Scrapers:")
    print("=" * 50)
    
    scrapers_found = False
    
    # Iterate through country directories
    for country_dir in sorted(configs_dir.iterdir()):
        if not country_dir.is_dir():
            continue
            
        country_name = country_dir.name
        config_files = list(country_dir.glob("*.yaml"))
        
        if config_files:
            scrapers_found = True
            print(f"\n🌍 {country_name.upper()}:")
            
            for config_file in sorted(config_files):
                newspaper_name = config_file.stem
                print(f"  📄 {newspaper_name}")
                print(f"     Command: python scripts/text/main.py {newspaper_name}")
    
    if not scrapers_found:
        print("No scrapers configured yet.")
    
    print("\n" + "=" * 50)


def list_countries():
    """List all available countries."""
    scrapers_dir = get_scrapers_dir()
    configs_dir = scrapers_dir / "configs"
    
    if not configs_dir.exists():
        print("❌ No configs directory found")
        return
    
    countries = [d.name for d in configs_dir.iterdir() if d.is_dir()]
    
    if countries:
        print("🌍 Available Countries:")
        print("=" * 30)
        for country in sorted(countries):
            print(f"  🏴 {country}")
        print("=" * 30)
    else:
        print("No countries configured yet.")


async def run_scraper_by_name(newspaper_name: str, country: str = None, update_mode: bool = False, **kwargs):
    """
    Run a scraper by newspaper name.
    
    Args:
        newspaper_name: Name of the newspaper to scrape
        country: Optional country filter
        update_mode: Whether to run in update mode (skip existing articles)
        **kwargs: Additional arguments for the scraper
    """
    scrapers_dir = get_scrapers_dir()
    
    # Find the config file
    config_files = find_config_files(
        get_default_configs_dir(),
        country=country,
        newspaper=newspaper_name
    )
    
    if not config_files:
        print(f"❌ No configuration found for newspaper '{newspaper_name}'")
        if country:
            print(f"   Searched in country: {country}")
        print("\nUse --list-scrapers to see available options.")
        return False
    
    if len(config_files) > 1:
        print(f"⚠️  Multiple configurations found for '{newspaper_name}':")
        for config_file in config_files:
            rel_path = config_file.relative_to(scrapers_dir / "configs")
            print(f"   {rel_path}")
        print(f"Using: {config_files[0].relative_to(scrapers_dir / 'configs')}")
    
    config_path = config_files[0]
    
    print(f"🚀 Starting scraper: {newspaper_name}")
    if country:
        print(f"🌍 Country: {country}")
    print(f"📁 Config: {config_path.relative_to(scrapers_dir)}")
    print("-" * 50)
    
    try:
        # Run the scraper
        results = await run_single_scraper(
            config_path=config_path,
            storage_dir=kwargs.get('storage_dir'),
            save_results=not kwargs.get('no_save', False),
            update_mode=update_mode
        )
        
        if results['success']:
            print("\n" + "=" * 50)
            print("✅ Scraping completed successfully!")
            
            stats = results.get('statistics', {})
            print(f"📊 Statistics:")
            print(f"   Articles scraped: {stats.get('articles_scraped', 0)}")
            print(f"   Thumbnails found: {stats.get('thumbnails_found', 0)}")
            print(f"   Failed URLs: {stats.get('failed_urls', 0)}")
            
            if 'timing' in results:
                duration = results['timing']['duration_seconds']
                print(f"⏱️  Duration: {duration:.1f} seconds")
            
            if 'saved_files' in results:
                print(f"💾 Saved files:")
                for file_type, file_path in results['saved_files'].items():
                    # Make path relative to project root for cleaner display
                    try:
                        rel_path = Path(file_path).relative_to(project_root)
                        print(f"   {file_type}: {rel_path}")
                    except ValueError:
                        print(f"   {file_type}: {file_path}")
            
            return True
        else:
            print("\n" + "=" * 50)
            print(f"❌ Scraping failed!")
            print(f"Error: {results.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"\n❌ Error running scraper: {e}")
        return False


def main():
    """Main entry point for the text scraping tools."""
    parser = argparse.ArgumentParser(
        description="Pacific Observatory - Newspaper Scraping Tools",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/text/main.py sibc                    # Run SIBC scraper (full mode)
  python scripts/text/main.py sibc --update           # Run SIBC scraper (update mode - skip existing articles)
  python scripts/text/main.py --list-scrapers         # List all available scrapers
  python scripts/text/main.py --list-countries        # List all countries
  python scripts/text/main.py sibc --no-save          # Run without saving results
        """
    )
    
    # Main arguments
    parser.add_argument(
        "newspaper",
        nargs="?",
        help="Name of the newspaper to scrape"
    )
    
    parser.add_argument(
        "--country",
        help="Country code filter (e.g., SB for Solomon Islands)"
    )
    
    # List options
    parser.add_argument(
        "--list-scrapers",
        action="store_true",
        help="List all available newspaper scrapers"
    )
    
    parser.add_argument(
        "--list-countries",
        action="store_true",
        help="List all available countries"
    )
    
    # Scraping options
    parser.add_argument(
        "--storage-dir",
        type=Path,
        help="Custom storage directory for results"
    )
    
    parser.add_argument(
        "--no-save",
        action="store_true",
        help="Don't save results to disk (dry run)"
    )
    
    parser.add_argument(
        "--update",
        action="store_true",
        help="Run in update mode (scrape URLs but skip articles that already exist in news.jsonl)"
    )
    
    # Logging options
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Logging level"
    )
    
    parser.add_argument(
        "--log-file",
        type=Path,
        help="Log file path"
    )
    
    args = parser.parse_args()
    
    # Set up logging
    setup_logging(args.log_level, args.log_file)
    
    # Handle list commands
    if args.list_scrapers:
        list_available_scrapers()
        return
    
    if args.list_countries:
        list_countries()
        return
    
    # Validate newspaper argument
    if not args.newspaper:
        parser.error("Newspaper name is required (or use --list-scrapers to see options)")
    
    # Run the scraper
    print("🌊 Pacific Observatory - Text Scraping Tools")
    print("=" * 50)
    
    try:
        success = asyncio.run(run_scraper_by_name(
            newspaper_name=args.newspaper,
            country=args.country,
            update_mode=args.update,
            storage_dir=args.storage_dir,
            no_save=args.no_save
        ))
        
        if not success:
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⚠️  Scraping interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()