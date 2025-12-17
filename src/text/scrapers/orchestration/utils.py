"""
Pacific Observatory - Orchestration Utilities

This module contains utility functions for the orchestration system,
including logging setup and path management.
"""

import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict


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


def get_project_paths() -> Dict[str, Path]:
    """
    Get all relevant project paths.

    This function calculates paths relative to this file's location.
    File is at: src/text/scrapers/orchestration/utils.py

    Returns:
        Dictionary with keys: script_dir, orchestration_dir, scrapers_dir,
        text_dir, src_dir, project_root
    """
    # Start from this file's location
    utils_file = Path(__file__).resolve()
    orchestration_dir = utils_file.parent  # orchestration/
    scrapers_dir = orchestration_dir.parent  # scrapers/
    text_dir = scrapers_dir.parent  # text/
    src_dir = text_dir.parent  # src/
    project_root = src_dir.parent  # project root

    return {
        "script_dir": orchestration_dir,  # For backward compatibility
        "orchestration_dir": orchestration_dir,
        "scrapers_dir": scrapers_dir,
        "text_dir": text_dir,
        "src_dir": src_dir,
        "project_root": project_root,
    }


def get_scrapers_dir() -> Path:
    """Get the scrapers directory path."""
    paths = get_project_paths()
    return paths["scrapers_dir"]


def get_default_configs_dir() -> Path:
    """Get the default configs directory path."""
    return get_scrapers_dir() / "configs"


def setup_python_path():
    """
    Add src directory to Python path if not already present.

    This is useful when running scripts directly without proper module imports.
    """
    paths = get_project_paths()
    src_dir = paths["src_dir"]

    if str(src_dir) not in sys.path:
        sys.path.insert(0, str(src_dir))


def create_progress_display():
    """
    Create a Rich progress display for monitoring scrapers.

    Returns:
        Tuple of (Progress object, Console object)
    """
    from rich.progress import (
        Progress,
        SpinnerColumn,
        TextColumn,
        TimeElapsedColumn,
    )
    from rich.console import Console

    console = Console()

    progress = Progress(
        SpinnerColumn(),
        TextColumn(
            "[bold blue]{task.fields[country]:20s}[/] / [cyan]{task.fields[newspaper]:20s}[/]"
        ),
        TextColumn("{task.description}"),
        TimeElapsedColumn(),
        console=console,
        transient=False,  # keep progress bars visible after completion
    )

    return progress, console


def get_scraper_log_path(
    country: str, newspaper: str, project_root: Optional[Path] = None
) -> Path:
    """
    Generate the log file path for a specific scraper.

    Args:
        country: Country code or name
        newspaper: Newspaper name
        project_root: Project root directory (defaults to calculated root)

    Returns:
        Path object for the log file: logs/text/country/newspaper/YYYYMMDD_HHMMSS.log
    """

    if project_root is None:
        project_root = get_project_paths()["project_root"]

    # Normalize newspaper name: lowercase and replace spaces with underscores
    normalized_newspaper = newspaper.lower().replace(" ", "_")

    # Create log directory structure
    log_dir = project_root / "logs" / "text" / country / normalized_newspaper
    log_dir.mkdir(parents=True, exist_ok=True)

    # Generate timestamp for log file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = log_dir / f"{timestamp}.log"

    return log_file


def add_file_handler_to_logger(
    log_file: Path, level: str = "INFO", logger_obj: Optional[logging.Logger] = None
) -> logging.FileHandler:
    """
    Add a file handler to the root logger or a specific logger.

    Args:
        log_file: Path to the log file
        level: Logging level for the file handler
        logger_obj: Specific logger object (defaults to root logger)

    Returns:
        The FileHandler object (can be removed later if needed)
    """
    # Create file handler
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(getattr(logging, level.upper()))

    # Set formatter to match console format
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    file_handler.setFormatter(formatter)

    # Add to logger
    if logger_obj is None:
        logger_obj = logging.getLogger()

    logger_obj.addHandler(file_handler)

    return file_handler
