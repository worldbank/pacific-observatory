"""
Orchestration script for running a single newspaper scraper.

This script provides the entry point for executing a scrape
for a single newspaper using its YAML configuration.
"""

import asyncio
import argparse
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

# Add the parent directory to the path so we can import our modules
scrapers_dir = Path(__file__).parent.parent
sys.path.insert(0, str(scrapers_dir))

# Import with absolute paths to avoid relative import issues
try:
    # First try importing as if we're running from the scrapers directory
    import factory
    import pipelines.storage
    create_scraper_from_file = factory.create_scraper_from_file
    find_config_files = factory.find_config_files
    get_default_configs_dir = factory.get_default_configs_dir
    JsonlStorage = pipelines.storage.JsonlStorage
except ImportError:
    # If that fails, try adding the scrapers directory to sys.path and importing directly
    import importlib.util
    
    # Import factory module
    factory_path = scrapers_dir / "factory.py"
    spec = importlib.util.spec_from_file_location("factory", factory_path)
    factory = importlib.util.module_from_spec(spec)
    sys.modules["factory"] = factory
    spec.loader.exec_module(factory)
    
    create_scraper_from_file = factory.create_scraper_from_file
    find_config_files = factory.find_config_files
    get_default_configs_dir = factory.get_default_configs_dir
    
    # Import storage module
    storage_path = scrapers_dir / "pipelines" / "storage.py"
    spec = importlib.util.spec_from_file_location("storage", storage_path)
    storage = importlib.util.module_from_spec(spec)
    sys.modules["storage"] = storage
    spec.loader.exec_module(storage)
    
    JsonlStorage = storage.JsonlStorage


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
    save_results: bool = True
) -> dict:
    """
    Run a single newspaper scraper.
    
    Args:
        config_path: Path to the newspaper configuration file
        storage_dir: Optional custom storage directory
        save_results: Whether to save results to disk
        
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
        logger.info(f"Starting scrape for {scraper.name} ({scraper.country})")
        start_time = datetime.now()
        
        results = await scraper.run_full_scrape()
        
        end_time = datetime.now()
        duration = end_time - start_time
        
        # Add timing information
        results['timing'] = {
            'start_time': start_time.isoformat(),
            'end_time': end_time.isoformat(),
            'duration_seconds': duration.total_seconds()
        }
        
        # Save results if requested
        if save_results and storage and results['success']:
            logger.info("Saving scraping results...")
            saved_files = storage.save_scraping_results(
                results, 
                scraper.country, 
                scraper.name,
                start_time
            )
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


async def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(
        description="Run a newspaper scraper from configuration file"
    )
    
    parser.add_argument(
        "config",
        nargs="?",
        help="Path to configuration file or newspaper name"
    )
    
    parser.add_argument(
        "--country",
        help="Country code (used with newspaper name to find config)"
    )
    
    parser.add_argument(
        "--storage-dir",
        type=Path,
        help="Custom storage directory for results"
    )
    
    parser.add_argument(
        "--no-save",
        action="store_true",
        help="Don't save results to disk"
    )
    
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
    
    parser.add_argument(
        "--list-configs",
        action="store_true",
        help="List available configuration files"
    )
    
    args = parser.parse_args()
    
    # Set up logging
    setup_logging(args.log_level, args.log_file)
    logger = logging.getLogger(__name__)
    
    # List configs if requested
    if args.list_configs:
        configs_dir = get_default_configs_dir()
        config_files = find_config_files(configs_dir)
        
        if config_files:
            print("Available configuration files:")
            for config_file in config_files:
                rel_path = config_file.relative_to(configs_dir)
                print(f"  {rel_path}")
        else:
            print(f"No configuration files found in {configs_dir}")
        
        return
    
    # Validate arguments
    if not args.config:
        parser.error("Configuration file or newspaper name is required")
    
    # Determine config file path
    config_path = Path(args.config)
    
    if not config_path.exists():
        # Try to find config by newspaper name
        configs_dir = get_default_configs_dir()
        config_files = find_config_files(configs_dir, args.country, args.config)
        
        if not config_files:
            logger.error(f"Configuration file not found: {args.config}")
            if args.country:
                logger.error(f"Searched for newspaper '{args.config}' in country '{args.country}'")
            sys.exit(1)
        
        if len(config_files) > 1:
            logger.warning(f"Multiple configs found for '{args.config}', using: {config_files[0]}")
        
        config_path = config_files[0]
    
    # Run the scraper
    logger.info("Starting newspaper scraping operation")
    
    try:
        results = await run_single_scraper(
            config_path,
            args.storage_dir,
            not args.no_save
        )
        
        # Print summary
        if results['success']:
            print(f"\n✅ Scraping completed successfully!")
            print(f"Newspaper: {results['newspaper']} ({results['country']})")
            
            if 'statistics' in results:
                stats = results['statistics']
                print(f"Articles scraped: {stats.get('articles_scraped', 0)}")
                print(f"Thumbnails found: {stats.get('thumbnails_found', 0)}")
                print(f"Failed URLs: {stats.get('failed_urls', 0)}")
            
            if 'timing' in results:
                duration = results['timing']['duration_seconds']
                print(f"Duration: {duration:.1f} seconds")
            
            if 'saved_files' in results:
                print("Saved files:")
                for file_type, file_path in results['saved_files'].items():
                    print(f"  {file_type}: {file_path}")
        
        else:
            print(f"\n❌ Scraping failed!")
            print(f"Error: {results.get('error', 'Unknown error')}")
            sys.exit(1)
    
    except KeyboardInterrupt:
        logger.info("Scraping interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
