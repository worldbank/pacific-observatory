"""
Pacific Observatory - Configuration Discovery

This module contains functions for discovering and organizing newspaper
scraper configurations.
"""

from pathlib import Path
from typing import List, Dict, Tuple
from collections import defaultdict


def discover_configs(configs_dir: Path) -> List[Dict[str, str]]:
    """
    Discover all YAML configuration files in the configs directory.

    Args:
        configs_dir: Path to the configs directory

    Returns:
        List of dictionaries with keys: 'country', 'newspaper', 'config_path'
    """
    discovered = []

    if not configs_dir.exists():
        return discovered

    # Iterate through country directories
    for country_dir in configs_dir.iterdir():
        if not country_dir.is_dir():
            continue

        country_name = country_dir.name

        # Find all YAML files, excluding template.yaml
        for config_file in country_dir.glob("*.yaml"):
            if config_file.name == "template.yaml":
                continue

            newspaper_name = config_file.stem
            discovered.append(
                {
                    "country": country_name,
                    "newspaper": newspaper_name,
                    "config_path": str(config_file),
                }
            )

    return discovered


def group_by_newspaper(
    configs: List[Dict[str, str]],
) -> Tuple[List[Dict], List[List[Dict]]]:
    """
    Group configurations by newspaper name to handle multi-country newspapers.

    Multi-country newspapers (appearing in >1 country) must run sequentially
    to avoid blocking issues.

    Args:
        configs: List of config dictionaries from discover_configs()

    Returns:
        Tuple of (single_country_configs, multi_country_groups)
        - single_country_configs: Configs that can run in parallel
        - multi_country_groups: Lists of configs that must run sequentially
    """
    # Group by newspaper name
    newspaper_groups = defaultdict(list)
    for config in configs:
        newspaper_groups[config["newspaper"]].append(config)

    single_country = []
    multi_country = []

    for newspaper_name, group in newspaper_groups.items():
        if len(group) == 1:
            single_country.append(group[0])
        else:
            # Multi-country newspaper - must run sequentially
            multi_country.append(group)

    return single_country, multi_country


def get_available_scrapers(configs_dir: Path) -> Dict[str, List[str]]:
    """
    Get all available newspaper scrapers organized by country.

    Args:
        configs_dir: Path to the configs directory

    Returns:
        Dictionary mapping country names to lists of newspaper names
        Example: {"solomon_islands": ["sibc", "solomon_star"], ...}
    """
    scrapers_by_country = defaultdict(list)

    if not configs_dir.exists():
        return dict(scrapers_by_country)

    # Iterate through country directories
    for country_dir in sorted(configs_dir.iterdir()):
        if not country_dir.is_dir():
            continue

        country_name = country_dir.name
        config_files = list(country_dir.glob("*.yaml"))

        # Exclude template.yaml
        config_files = [f for f in config_files if f.name != "template.yaml"]

        if config_files:
            newspapers = [config_file.stem for config_file in sorted(config_files)]
            scrapers_by_country[country_name] = newspapers

    return dict(scrapers_by_country)


def get_available_countries(configs_dir: Path) -> List[str]:
    """
    Get all available countries.

    Args:
        configs_dir: Path to the configs directory

    Returns:
        List of country names
    """
    if not configs_dir.exists():
        return []

    countries = [d.name for d in configs_dir.iterdir() if d.is_dir()]
    return sorted(countries)
