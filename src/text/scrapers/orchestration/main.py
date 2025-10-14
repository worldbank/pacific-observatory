#!/usr/bin/env python3
"""
Pacific Observatory - Text Scraping CLI Entry Point

This script provides a command-line interface for running newspaper scrapers
using the new config-driven architecture.

Usage:
    python src/text/scrapers/orchestration/main.py --help
    python src/text/scrapers/orchestration/main.py sibc
    python src/text/scrapers/orchestration/main.py --list-scrapers
    python src/text/scrapers/orchestration/main.py --list-countries
"""

import asyncio
import argparse
import os
import sys
from pathlib import Path
import logging
from typing import Optional

# Set up the data folder path
os.environ["DATA_FOLDER_PATH"] = "data/text"

# Add the src directory to Python path for imports
# File is at: src/text/scrapers/orchestration/main.py
# Go up 4 levels to get to src/, then up 1 more to project root
script_dir = Path(__file__).resolve().parent  # orchestration/
scrapers_dir = script_dir.parent  # scrapers/
text_dir = scrapers_dir.parent  # text/
src_dir = text_dir.parent  # src/
project_root = src_dir.parent  # project root

if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

# Import scraper execution functions (after path setup)
from text.scrapers.orchestration.run_scraper import run_scraper_by_name


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
        handlers=handlers,
    )


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
                print(
                    f"     Command: python src/text/scrapers/orchestration/main.py {newspaper_name}"
                )

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


def main():
    """Main entry point for the text scraping tools."""
    parser = argparse.ArgumentParser(
        description="Pacific Observatory - Newspaper Scraping Tools",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python src/text/scrapers/orchestration/main.py sibc                    # Run SIBC scraper (full mode)
  python src/text/scrapers/orchestration/main.py sibc --update           # Run SIBC scraper (update mode - skip existing articles)
  python src/text/scrapers/orchestration/main.py --list-scrapers         # List all available scrapers
  python src/text/scrapers/orchestration/main.py --list-countries        # List all countries
  python src/text/scrapers/orchestration/main.py sibc --no-save          # Run without saving results
        """,
    )

    # Main arguments
    parser.add_argument(
        "newspaper", nargs="?", help="Name of the newspaper to scrape"
    )

    parser.add_argument(
        "--country", help="Country code filter (e.g., SB for Solomon Islands)"
    )

    # List options
    parser.add_argument(
        "--list-scrapers",
        action="store_true",
        help="List all available newspaper scrapers",
    )

    parser.add_argument(
        "--list-countries",
        action="store_true",
        help="List all available countries",
    )

    # Scraping options
    parser.add_argument(
        "--storage-dir", type=Path, help="Custom storage directory for results"
    )

    parser.add_argument(
        "--no-save",
        action="store_true",
        help="Don't save results to disk (dry run)",
    )

    parser.add_argument(
        "--update",
        default=True,
        action="store_true",
        help="Run in update mode (scrape URLs but skip articles that already exist in news.jsonl)",
    )

    # Logging options
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Logging level",
    )

    parser.add_argument("--log-file", type=Path, help="Log file path")

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
        parser.error(
            "Newspaper name is required (or use --list-scrapers to see options)"
        )

    # Run the scraper
    print("🌊 Pacific Observatory - Text Scraping Tools")
    print("=" * 50)

    try:
        success, results = asyncio.run(
            run_scraper_by_name(
                newspaper_name=args.newspaper,
                country=args.country,
                update_mode=args.update,
                configs_dir=get_default_configs_dir(),
                project_root=project_root,
                storage_dir=args.storage_dir,
                no_save=args.no_save,
            )
        )

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

