"""
Pacific Observatory - Orchestration Utilities

This module contains utility functions for the orchestration system,
including logging setup and path management.
"""

import logging
import sys
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
