# Pacific Observatory - Text Scraping Tools

This directory contains the main entry point for running newspaper scrapers using the new config-driven architecture.

## Quick Start

From the main `pacific-observatory` directory, you can run:

```bash
# List all available scrapers
python src/text/scrapers/orchestration/main.py --list-scrapers

# List all countries
python src/text/scrapers/orchestration/main.py --list-countries

# Run the SIBC scraper
python src/text/scrapers/orchestration/main.py sibc
```

## Available Commands

### List Commands
- `--list-scrapers` - Show all configured newspaper scrapers
- `--list-countries` - Show all available countries

### Scraping Commands
- `<newspaper_name>` - Run a specific newspaper scraper
- `--storage-dir <path>` - Custom storage directory
- `--no-save` - Dry run without saving results

### Logging Options
- `--log-level <level>` - Set logging level (DEBUG, INFO, WARNING, ERROR)
- `--log-file <path>` - Save logs to file

## Examples

```bash
# Basic usage
python src/text/scrapers/orchestration/main.py sibc

# Basic usage with update
python src/text/scrapers/orchestration/main.py sibc --update

# Dry run (no saving)
python src/text/scrapers/orchestration/main.py sibc --no-save

# With debug logging
python src/text/scrapers/orchestration/main.py sibc --log-level DEBUG

# Save logs to file
python src/text/scrapers/orchestration/main.py sibc --log-file logs/sibc.log

# Custom storage location
python src/text/scrapers/orchestration/main.py sibc --storage-dir /path/to/custom/storage
```

## Adding New Scrapers

To add a new newspaper scraper:

1. Create a YAML configuration file in `src/text/scrapers/configs/<country>/<newspaper>.yaml`
2. Define the selectors, listing strategy, and other parameters
3. The scraper will automatically be available through this interface

See `src/text/scrapers/configs/solomon_islands/sibc.yaml` for an example configuration.

## Architecture

This interface uses the new config-driven scraping framework located in `src/text/scrapers/`. The framework provides:

- **Async HTTP client** for high-performance scraping
- **Dynamic pagination detection** 
- **Pydantic data validation**
- **Modular, reusable components**
- **YAML-based configuration**
- **Consistent data storage**

For more details, see the documentation in `src/text/scrapers/`.
