"""
Pacific Observatory - Scraper Execution Functions

This module contains all the core scraper execution logic, separated from CLI handling.
"""

import asyncio
import logging
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict

# Set up Python path for imports when run as a script
# This needs to happen before any text.* imports
if __name__ == "__main__":
    script_dir = Path(__file__).resolve().parent  # orchestration/
    scrapers_dir = script_dir.parent  # scrapers/
    text_dir = scrapers_dir.parent  # text/
    src_dir = text_dir.parent  # src/
    
    if str(src_dir) not in sys.path:
        sys.path.insert(0, str(src_dir))

from text.scrapers.factory import create_scraper_from_file, find_config_files
from text.scrapers.pipelines.storage import JsonlStorage


async def run_single_scraper(
    config_path: Path,
    storage_dir: Optional[Path] = None,
    save_results: bool = True,
    update_mode: bool = False,
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
            logger.info(
                f"Starting UPDATE scrape for {scraper.name} ({scraper.country})"
            )
        else:
            logger.info(
                f"Starting FULL scrape for {scraper.name} ({scraper.country})"
            )
        start_time = datetime.now()

        if update_mode:
            results = await scraper.run_update_scrape()
        else:
            results = await scraper.run_full_scrape()

        end_time = datetime.now()
        duration = end_time - start_time

        # Add timing information
        results["timing"] = {
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "duration_seconds": duration.total_seconds(),
        }

        # Results are already saved by the scraper itself
        # Just get the file paths from the scraper
        if save_results and results["success"]:
            saved_files = getattr(scraper, "_saved_files", {})
            results["saved_files"] = {
                str(k): str(v) for k, v in saved_files.items()
            }

        # Clean up resources
        scraper.cleanup()

        # Log summary
        if results["success"]:
            stats = results["statistics"]
            logger.info(
                f"Scraping completed successfully in {duration.total_seconds():.1f}s: "
            )
        else:
            logger.error(
                f"Scraping failed: {results.get('error', 'Unknown error')}"
            )

        return results

    except Exception as e:
        logger.error(f"Error running scraper: {e}")
        return {
            "success": False,
            "error": str(e),
            "newspaper": (
                getattr(scraper, "name", "Unknown")
                if "scraper" in locals()
                else "Unknown"
            ),
            "country": (
                getattr(scraper, "country", "Unknown")
                if "scraper" in locals()
                else "Unknown"
            ),
        }


async def run_scraper_by_name(
    newspaper_name: str,
    country: str = None,
    update_mode: bool = False,
    configs_dir: Path = None,
    project_root: Path = None,
    **kwargs,
):
    """
    Run a scraper by newspaper name.

    Args:
        newspaper_name: Name of the newspaper to scrape
        country: Optional country filter
        update_mode: Whether to run in update mode (skip existing articles)
        configs_dir: Directory containing config files
        project_root: Project root directory for relative path display
        **kwargs: Additional arguments for the scraper

    Returns:
        Tuple of (success: bool, results: dict)
    """
    # Find the config file
    config_files = find_config_files(
        configs_dir, country=country, newspaper=newspaper_name
    )

    if not config_files:
        print(f"❌ No configuration found for newspaper '{newspaper_name}'")
        if country:
            print(f"   Searched in country: {country}")
        print("\nUse --list-scrapers to see available options.")
        return False, None

    if len(config_files) > 1:
        print(f"⚠️  Multiple configurations found for '{newspaper_name}':")
        for config_file in config_files:
            rel_path = config_file.relative_to(configs_dir)
            print(f"   {rel_path}")
        print(f"Using: {config_files[0].relative_to(configs_dir)}")

    config_path = config_files[0]

    print(f"🚀 Starting scraper: {newspaper_name}")
    if country:
        print(f"🌍 Country: {country}")
    if configs_dir:
        print(f"📁 Config: {config_path.relative_to(configs_dir.parent)}")
    print("-" * 50)

    try:
        # Run the scraper
        results = await run_single_scraper(
            config_path=config_path,
            storage_dir=kwargs.get("storage_dir"),
            save_results=not kwargs.get("no_save", False),
            update_mode=update_mode,
        )

        if results["success"]:
            print("\n" + "=" * 50)
            print("✅ Scraping completed successfully!")

            stats = results.get("statistics", {})
            print(f"📊 Statistics:")
            print(f"   Articles scraped: {stats.get('articles_scraped', 0)}")
            print(f"   Thumbnails found: {stats.get('thumbnails_found', 0)}")
            print(f"   Failed URLs: {stats.get('failed_urls', 0)}")

            if "timing" in results:
                duration = results["timing"]["duration_seconds"]
                print(f"⏱️  Duration: {duration:.1f} seconds")

            if "saved_files" in results and project_root:
                print(f"💾 Saved files:")
                for file_type, file_path in results["saved_files"].items():
                    # Make path relative to project root for cleaner display
                    try:
                        rel_path = Path(file_path).relative_to(project_root)
                        print(f"   {file_type}: {rel_path}")
                    except ValueError:
                        print(f"   {file_type}: {file_path}")

            return True, results
        else:
            print("\n" + "=" * 50)
            print(f"❌ Scraping failed!")
            print(f"Error: {results.get('error', 'Unknown error')}")
            return False, results

    except Exception as e:
        print(f"\n❌ Error running scraper: {e}")
        return False, None


def run_sequential_group_cli(
    group_configs: List[Dict[str, str]],
    project_root: Path,
    log_dir: Path,
):
    """
    CLI entry point for running a multi-country newspaper group sequentially.
    
    This function is designed to be called from a subprocess and runs each
    country's scraper sequentially to avoid rate limiting.
    
    Args:
        group_configs: List of config dictionaries with 'country' and 'newspaper' keys
        project_root: Project root directory
        log_dir: Base log directory
    
    Returns:
        Exit code (0 for success, 1 for any failures)
    """
    # Set up minimal logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )
    
    exit_code = 0
    
    for config in group_configs:
        country = config["country"]
        newspaper = config["newspaper"]
        
        # Create log directory
        log_subdir = log_dir / country / newspaper
        log_subdir.mkdir(parents=True, exist_ok=True)
        
        # Generate timestamp for log file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = log_subdir / f"{timestamp}.log"
        
        # Set up file logging for this scraper
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(
            logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        )
        logger = logging.getLogger()
        logger.addHandler(file_handler)
        
        try:
            logging.info(f"Starting {country}/{newspaper}...")
            
            # Run the scraper
            success, results = asyncio.run(
                run_scraper_by_name(
                    newspaper_name=newspaper,
                    country=country,
                    update_mode=True,
                    configs_dir=project_root / "src" / "text" / "scrapers" / "configs",
                    project_root=project_root,
                )
            )
            
            if not success:
                logging.error(f"Failed to run {country}/{newspaper}")
                exit_code = 1
            else:
                logging.info(f"Completed {country}/{newspaper}")
        
        except Exception as e:
            logging.error(f"Error running {country}/{newspaper}: {e}")
            exit_code = 1
        
        finally:
            # Remove file handler
            logger.removeHandler(file_handler)
            file_handler.close()
        
        # Small delay between countries in the same group
        time.sleep(1)
    
    return exit_code


if __name__ == "__main__":
    """
    CLI entry point for running sequential groups.
    
    Usage:
        python run_scraper.py \
            --group "country1,newspaper1;country2,newspaper2" \
            --project-root /path/to/project \
            --log-dir /path/to/logs
    """
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Run a multi-country newspaper group sequentially"
    )
    parser.add_argument(
        "--group",
        required=True,
        help="Semicolon-separated list of country,newspaper pairs",
    )
    parser.add_argument(
        "--project-root",
        required=True,
        type=Path,
        help="Project root directory",
    )
    parser.add_argument(
        "--log-dir",
        required=True,
        type=Path,
        help="Base log directory",
    )
    
    args = parser.parse_args()
    
    # Parse group configs
    group_configs = []
    for config_str in args.group.split(";"):
        country, newspaper = config_str.split(",")
        group_configs.append({
            "country": country,
            "newspaper": newspaper,
        })
    
    # Run the group
    exit_code = run_sequential_group_cli(
        group_configs=group_configs,
        project_root=args.project_root,
        log_dir=args.log_dir,
    )
    
    sys.exit(exit_code)
