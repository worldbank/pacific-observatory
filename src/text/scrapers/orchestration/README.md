# Pacific Observatory - Text Scraping Tools

This directory contains the main entry point for running newspaper scrapers using the new config-driven architecture.

## Quick Start

From the main `pacific-observatory` directory, you can run:

```bash
# List all available scrapers
poetry run python src/text/scrapers/orchestration/main.py --list-scrapers

# List all countries
poetry run python src/text/scrapers/orchestration/main.py --list-countries

# Run the SIBC scraper
poetry run python src/text/scrapers/orchestration/main.py sibc

# Run ALL scrapers in parallel
poetry run python src/text/scrapers/orchestration/main.py --run-all
```

## Available Commands

### List Commands
- `--list-scrapers` - Show all configured newspaper scrapers
- `--list-countries` - Show all available countries

### Single Scraper Commands
- `<newspaper_name>` - Run a specific newspaper scraper
- `--update` - Run in update mode (skip existing articles)
- `--storage-dir <path>` - Custom storage directory
- `--no-save` - Dry run without saving results

### Multi-Scraper Runner Commands
- `--run-all` - Run all newspaper scrapers in parallel
- `--sequential` - Force sequential execution (for debugging, use with --run-all)
- `--dry-run` - Preview what would run without executing (use with --run-all)

### Logging Options
- `--log-level <level>` - Set logging level (DEBUG, INFO, WARNING, ERROR)
- `--log-file <path>` - Save logs to file

## Examples

### Single Scraper

```bash
# Basic usage
poetry run python src/text/scrapers/orchestration/main.py sibc

# Update mode (skip existing articles)
poetry run python src/text/scrapers/orchestration/main.py sibc --update

# Dry run (no saving)
poetry run python src/text/scrapers/orchestration/main.py sibc --no-save

# With debug logging
poetry run python src/text/scrapers/orchestration/main.py sibc --log-level DEBUG

# Save logs to file
poetry run python src/text/scrapers/orchestration/main.py sibc --log-file logs/sibc.log

# Custom storage location
poetry run python src/text/scrapers/orchestration/main.py sibc --storage-dir /path/to/custom/storage
```

### Multi-Scraper Runner

```bash
# Run all scrapers in parallel (recommended)
poetry run python src/text/scrapers/orchestration/main.py --run-all

# Run all scrapers sequentially (for debugging)
poetry run python src/text/scrapers/orchestration/main.py --run-all --sequential

# Preview what would run without executing
poetry run python src/text/scrapers/orchestration/main.py --run-all --dry-run
```

## Adding New Scrapers

To add a new newspaper scraper:

1. Create a YAML configuration file in `src/text/scrapers/configs/<country>/<newspaper>.yaml`
2. Define the selectors, listing strategy, and other parameters
3. The scraper will automatically be available through this interface

See `src/text/scrapers/configs/solomon_islands/sibc.yaml` for an example configuration.

## Multi-Scraper Runner

The `--run-all` command runs all configured newspaper scrapers automatically in parallel, with intelligent handling of multi-country newspapers.

### Features

- **Parallel Execution**: Runs multiple scrapers simultaneously for faster completion
- **Multi-Country Handling**: Newspapers appearing in multiple countries run sequentially to avoid blocking
- **Independent Processes**: Each scraper runs as a separate subprocess with `nohup`-like behavior
- **Structured Logging**: Each scraper logs to its own file: `logs/{country}/{newspaper}/{timestamp}.log`
- **Real-Time Monitoring**: Shows completion status as scrapers finish
- **Robust Error Handling**: Continues running all scrapers even if some fail
- **Comprehensive Summary**: Displays a compact table with success/warning/failure counts

### Log Structure

```
logs/
├── solomon_islands/
│   ├── sibc/
│   │   └── 20251014_103000.log
│   └── solomon_star/
│       └── 20251014_103000.log
├── australia/
│   └── abc/
│       └── 20251014_103000.log
```

### Status Detection

The runner automatically detects scraper status by analyzing:
- **Exit codes**: Non-zero = failed
- **Log content**: Looks for warnings, exceptions, and success indicators
- **Output validation**: Checks for expected completion messages

Status categories:
- ✅ **Success**: Completed without warnings
- ⚠️ **Warning**: Completed but with warnings or exceptions in logs
- ❌ **Failed**: Non-zero exit code or missing expected output

### Multi-Country Newspapers

Some newspapers (e.g., ABC, RNZ) may appear in multiple countries. To avoid blocking issues:
- The runner automatically detects these by grouping configs by newspaper name
- Newspapers appearing in >1 country run **sequentially** within their group
- Single-country newspapers run in **parallel** with other scrapers

### Example Output

```
🌊 Pacific Observatory - Multi-Scraper Runner
============================================================

🔍 Discovering configurations...
   Found 4 scraper configuration(s)
   - 3 single-country newspapers
   - 1 multi-country newspaper groups

🚀 Starting 3 single-country scraper(s)...
   Starting solomon_islands/sibc...
   Starting solomon_islands/solomon_star...
   Starting fiji/fiji_times...

🔗 Processing 1 multi-country newspaper group(s)...

   Group: abc (2 countries)
      Starting australia/abc...

🔄 Monitoring 4 scraper(s)...

✅ solomon_islands/sibc completed (success)
⚠️  solomon_islands/solomon_star completed (warning)
✅ fiji/fiji_times completed (success)
✅ australia/abc completed (success)

────────────────────────────────────────────────────────────
SCRAPER SUMMARY (2025-10-14 10:45:00)
────────────────────────────────────────────────────────────
✅ australia          / abc                  Completed successfully
✅ fiji               / fiji_times           Completed successfully
✅ solomon_islands    / sibc                 Completed successfully
⚠️  solomon_islands    / solomon_star         Completed with warnings
────────────────────────────────────────────────────────────
Total: 4 | Success: 3 | Warnings: 1 | Failed: 0
────────────────────────────────────────────────────────────
```

### Automation

For automated daily/weekly runs, you can use:

#### Cron (Linux/Mac)

```bash
# Run daily at 2 AM
0 2 * * * cd /path/to/pacific-observatory && poetry run python src/text/scrapers/orchestration/main.py --run-all >> logs/cron.log 2>&1
```

#### Systemd Timer (Linux)

Create `/etc/systemd/system/pacific-scrapers.service`:
```ini
[Unit]
Description=Pacific Observatory Newspaper Scrapers

[Service]
Type=oneshot
WorkingDirectory=/path/to/pacific-observatory
ExecStart=/usr/bin/poetry run python src/text/scrapers/orchestration/main.py --run-all
User=your-user
```

Create `/etc/systemd/system/pacific-scrapers.timer`:
```ini
[Unit]
Description=Run Pacific Observatory scrapers daily

[Timer]
OnCalendar=daily
Persistent=true

[Install]
WantedBy=timers.target
```

Enable: `sudo systemctl enable --now pacific-scrapers.timer`

#### GitHub Actions

Create `.github/workflows/scrapers.yml`:
```yaml
name: Run Newspaper Scrapers

on:
  schedule:
    - cron: '0 2 * * *'  # Daily at 2 AM UTC
  workflow_dispatch:  # Manual trigger

jobs:
  scrape:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install Poetry
        run: pip install poetry
      - name: Install dependencies
        run: poetry install
      - name: Run scrapers
        run: poetry run python src/text/scrapers/orchestration/main.py --run-all
      - name: Upload logs
        uses: actions/upload-artifact@v3
        with:
          name: scraper-logs
          path: logs/
```

#### Apache Airflow

Create a DAG:
```python
from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta

default_args = {
    'owner': 'pacific-observatory',
    'depends_on_past': False,
    'start_date': datetime(2025, 1, 1),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'pacific_scrapers',
    default_args=default_args,
    schedule_interval='0 2 * * *',  # Daily at 2 AM
    catchup=False,
)

run_scrapers = BashOperator(
    task_id='run_all_scrapers',
    bash_command='cd /path/to/pacific-observatory && poetry run python src/text/scrapers/orchestration/main.py --run-all',
    dag=dag,
)
```

## Architecture

This interface uses the new config-driven scraping framework located in `src/text/scrapers/`. The framework provides:

- **Async HTTP client** for high-performance scraping
- **Dynamic pagination detection** 
- **Pydantic data validation**
- **Modular, reusable components**
- **YAML-based configuration**
- **Consistent data storage**
- **Multi-scraper orchestration** with parallel execution and intelligent grouping

For more details, see the documentation in `src/text/scrapers/`.
