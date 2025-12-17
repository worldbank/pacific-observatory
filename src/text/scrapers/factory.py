"""
Factory functions for creating scraper instances from configuration files.

This module provides factory functions that read YAML configuration files
and instantiate the appropriate scraper objects.
"""

import yaml
from pathlib import Path
from typing import Dict, Any, Optional, Union, List
import logging
from .newspaper_scraper import NewspaperScraper
from .models import NewspaperConfig

logger = logging.getLogger(__name__)


def load_yaml_config(config_path: Union[str, Path]) -> Dict[str, Any]:
    """
    Load and parse a YAML configuration file.

    Args:
        config_path: Path to the YAML configuration file

    Returns:
        Dictionary containing the parsed configuration

    Raises:
        FileNotFoundError: If the config file doesn't exist
        yaml.YAMLError: If the YAML is invalid
    """
    config_path = Path(config_path)

    if not config_path.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")

    try:
        with open(config_path, "r", encoding="utf-8") as file:
            config = yaml.safe_load(file)

        if not isinstance(config, dict):
            raise ValueError("Configuration file must contain a YAML dictionary")

        logger.info(f"Loaded configuration from: {config_path}")
        return config

    except yaml.YAMLError as e:
        logger.error(f"Invalid YAML in configuration file {config_path}: {e}")
        raise
    except Exception as e:
        logger.error(f"Error reading configuration file {config_path}: {e}")
        raise


def validate_config(config: Dict[str, Any]) -> NewspaperConfig:
    """
    Validate configuration against the NewspaperConfig model.

    Args:
        config: Configuration dictionary

    Returns:
        Validated NewspaperConfig instance

    Raises:
        ValidationError: If configuration is invalid
    """
    try:
        validated_config = NewspaperConfig(**config)
        logger.info(f"Configuration validated for newspaper: {validated_config.name}")
        return validated_config
    except Exception as e:
        logger.error(f"Configuration validation failed: {e}")
        raise


def create_scraper_from_config(
    config: Dict[str, Any], urls_from_scratch: bool = True
) -> NewspaperScraper:
    """
    Create a NewspaperScraper instance from a configuration dictionary.

    Args:
        config: Configuration dictionary
        urls_from_scratch: Whether to discover URLs from scratch (True) or load from urls.csv (False)

    Returns:
        NewspaperScraper instance

    Raises:
        ValidationError: If configuration is invalid
    """
    # Validate the configuration first
    validate_config(config)

    # Create and return the scraper
    scraper = NewspaperScraper(config, urls_from_scratch=urls_from_scratch)
    logger.info(f"Created scraper for {scraper.name} ({scraper.country})")

    return scraper


def create_scraper_from_file(
    config_path: Union[str, Path], urls_from_scratch: bool = True
) -> NewspaperScraper:
    """
    Create a NewspaperScraper instance from a YAML configuration file.

    Args:
        config_path: Path to the YAML configuration file
        urls_from_scratch: Whether to discover URLs from scratch (True) or load from urls.csv (False)

    Returns:
        NewspaperScraper instance

    Raises:
        FileNotFoundError: If the config file doesn't exist
        yaml.YAMLError: If the YAML is invalid
        ValidationError: If configuration is invalid
    """
    # Load the configuration
    config = load_yaml_config(config_path)

    # Add the config file path to the configuration for reference
    config["_config_path"] = str(Path(config_path).absolute())

    # Create and return the scraper
    return create_scraper_from_config(config, urls_from_scratch=urls_from_scratch)


def find_config_files(
    configs_dir: Union[str, Path],
    country: Optional[str] = None,
    newspaper: Optional[str] = None,
) -> List[Path]:
    """
    Find configuration files in the configs directory.

    Args:
        configs_dir: Path to the configs directory
        country: Optional country filter (directory name)
        newspaper: Optional newspaper filter (filename without extension)

    Returns:
        List of paths to matching configuration files
    """
    configs_dir = Path(configs_dir)

    if not configs_dir.exists():
        logger.warning(f"Configs directory not found: {configs_dir}")
        return []

    config_files = []

    # Search pattern based on filters
    if country and newspaper:
        # Look for specific newspaper in specific country
        pattern = configs_dir / country / f"{newspaper}.yaml"
        if pattern.exists():
            config_files.append(pattern)
    elif country:
        # Look for all newspapers in specific country
        country_dir = configs_dir / country
        if country_dir.exists():
            config_files.extend(country_dir.glob("*.yaml"))
    elif newspaper:
        # Look for specific newspaper in any country
        config_files.extend(configs_dir.rglob(f"{newspaper}.yaml"))
    else:
        # Find all configuration files
        config_files.extend(configs_dir.rglob("*.yaml"))

    logger.info(f"Found {len(config_files)} configuration files")
    return sorted(config_files)


def create_scrapers_from_directory(
    configs_dir: Union[str, Path],
    country: Optional[str] = None,
    newspaper: Optional[str] = None,
) -> List[NewspaperScraper]:
    """
    Create multiple scraper instances from configuration files in a directory.

    Args:
        configs_dir: Path to the configs directory
        country: Optional country filter
        newspaper: Optional newspaper filter

    Returns:
        List of NewspaperScraper instances
    """
    config_files = find_config_files(configs_dir, country, newspaper)
    scrapers = []

    for config_file in config_files:
        try:
            scraper = create_scraper_from_file(config_file)
            scrapers.append(scraper)
        except Exception as e:
            logger.error(f"Failed to create scraper from {config_file}: {e}")

    logger.info(
        f"Created {len(scrapers)} scrapers from {len(config_files)} config files"
    )
    return scrapers


def get_default_configs_dir() -> Path:
    """
    Get the default configs directory path.

    Returns:
        Path to the default configs directory
    """
    # Get the directory where this factory.py file is located
    current_dir = Path(__file__).parent

    # Look for configs directory relative to the scrapers directory
    configs_dir = current_dir / "configs"

    # If not found, try one level up (in case configs is at the same level as scrapers)
    if not configs_dir.exists():
        configs_dir = current_dir.parent / "configs"

    return configs_dir


def create_scraper(
    newspaper: Optional[str] = None,
    country: Optional[str] = None,
    config_path: Optional[Union[str, Path]] = None,
    config_dict: Optional[Dict[str, Any]] = None,
    urls_from_scratch: bool = True,
) -> NewspaperScraper:
    """
    Convenience function to create a scraper with flexible input options.

    Args:
        newspaper: Newspaper name (for auto-finding config file)
        country: Country code (for auto-finding config file)
        config_path: Explicit path to configuration file
        config_dict: Configuration dictionary (bypasses file loading)
        urls_from_scratch: Whether to discover URLs from scratch (True) or load from urls.csv (False)

    Returns:
        NewspaperScraper instance

    Raises:
        ValueError: If insufficient parameters provided
        FileNotFoundError: If config file not found
    """
    if config_dict:
        # Create from dictionary
        return create_scraper_from_config(
            config_dict, urls_from_scratch=urls_from_scratch
        )

    elif config_path:
        # Create from explicit file path
        return create_scraper_from_file(
            config_path, urls_from_scratch=urls_from_scratch
        )

    elif newspaper:
        # Auto-find config file
        configs_dir = get_default_configs_dir()
        config_files = find_config_files(configs_dir, country, newspaper)

        if not config_files:
            raise FileNotFoundError(
                f"No configuration file found for newspaper '{newspaper}'"
                + (f" in country '{country}'" if country else "")
            )

        if len(config_files) > 1:
            logger.warning(
                f"Multiple config files found for '{newspaper}', using first: {config_files[0]}"
            )

        return create_scraper_from_file(
            config_files[0], urls_from_scratch=urls_from_scratch
        )

    else:
        raise ValueError(
            "Must provide either config_dict, config_path, or newspaper name"
        )


# Convenience aliases
load_config = load_yaml_config
create_from_file = create_scraper_from_file
create_from_config = create_scraper_from_config
