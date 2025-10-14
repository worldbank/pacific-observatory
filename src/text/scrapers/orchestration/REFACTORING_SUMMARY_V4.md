# Orchestration Module Refactoring - Version 4

## Date
October 14, 2025

## Objective
Ensure `main.py` contains only CLI-related code by extracting utility and discovery functions into dedicated modules.

## Problem Statement

### Before
`main.py` contained a mix of CLI code and utility/discovery functions:
- CLI argument parsing ✅
- Command routing ✅
- Logging setup ❌ (utility function)
- Path management ❌ (utility functions)
- Scraper discovery ❌ (business logic)
- Country listing ❌ (business logic)

This violated the single responsibility principle and made code reuse difficult.

## Solution

### Created Two New Modules

#### 1. `utils.py` - Utility Functions
**Purpose:** Reusable utility functions for logging and path management

**Functions:**
- `setup_logging()` - Configure logging
- `get_project_paths()` - Get all project paths
- `get_scrapers_dir()` - Get scrapers directory
- `get_default_configs_dir()` - Get configs directory
- `setup_python_path()` - Add src to Python path

#### 2. `discovery.py` - Configuration Discovery
**Purpose:** Discover and organize newspaper configurations

**Functions:**
- `discover_configs()` - Find all YAML configs (moved from `run_multiple.py`)
- `group_by_newspaper()` - Group configs by newspaper (moved from `run_multiple.py`)
- `get_available_scrapers()` - Get scrapers by country (refactored from `main.py`)
- `get_available_countries()` - Get all countries (refactored from `main.py`)

## Changes Made

### 1. Created `utils.py` (95 lines)

```python
"""
Pacific Observatory - Orchestration Utilities

Utility functions for logging setup and path management.
"""

def setup_logging(level: str = "INFO", log_file: Optional[Path] = None):
    """Set up logging configuration."""
    # ... implementation

def get_project_paths() -> Dict[str, Path]:
    """Get all relevant project paths."""
    # Returns: script_dir, orchestration_dir, scrapers_dir, text_dir, src_dir, project_root

def get_scrapers_dir() -> Path:
    """Get the scrapers directory path."""

def get_default_configs_dir() -> Path:
    """Get the default configs directory path."""

def setup_python_path():
    """Add src directory to Python path."""
```

**Benefits:**
- Centralized path management
- Reusable across all orchestration modules
- Single source of truth for directory structure

### 2. Created `discovery.py` (139 lines)

```python
"""
Pacific Observatory - Configuration Discovery

Functions for discovering and organizing newspaper configurations.
"""

def discover_configs(configs_dir: Path) -> List[Dict[str, str]]:
    """Discover all YAML configuration files."""
    # Returns list of {country, newspaper, config_path}

def group_by_newspaper(configs: List[Dict[str, str]]) -> Tuple[List[Dict], List[List[Dict]]]:
    """Group configurations by newspaper name."""
    # Returns (single_country_configs, multi_country_groups)

def get_available_scrapers(configs_dir: Path) -> Dict[str, List[str]]:
    """Get all available scrapers organized by country."""
    # Returns {country: [newspapers]}

def get_available_countries(configs_dir: Path) -> List[str]:
    """Get all available countries."""
    # Returns sorted list of country names
```

**Benefits:**
- Separation of data retrieval from presentation
- Reusable discovery logic
- Testable without CLI
- No code duplication

### 3. Refactored `main.py`

**Removed:**
- `setup_logging()` → Moved to `utils.py`
- `get_scrapers_dir()` → Moved to `utils.py`
- `get_default_configs_dir()` → Moved to `utils.py`
- `list_available_scrapers()` → Refactored (now a thin CLI wrapper)
- `list_countries()` → Refactored (now a thin CLI wrapper)

**New Structure:**
```python
# main.py (CLI only)

from text.scrapers.orchestration.utils import (
    setup_logging,
    get_project_paths,
    get_default_configs_dir,
)
from text.scrapers.orchestration.discovery import (
    get_available_scrapers,
    get_available_countries,
)
from text.scrapers.orchestration.run_scraper import run_scraper_by_name
from text.scrapers.orchestration.run_multiple import run_all_scrapers

# Get project paths
paths = get_project_paths()
project_root = paths["project_root"]


def list_available_scrapers():
    """CLI wrapper: List all available newspaper scrapers."""
    scrapers = get_available_scrapers(get_default_configs_dir())
    
    if not scrapers:
        print("❌ No scrapers found")
        return
    
    # Print formatted output
    for country_name, newspapers in scrapers.items():
        print(f"\n🌍 {country_name.upper()}:")
        for newspaper_name in newspapers:
            print(f"  📄 {newspaper_name}")


def list_countries():
    """CLI wrapper: List all available countries."""
    countries = get_available_countries(get_default_configs_dir())
    
    # Print formatted output
    for country in countries:
        print(f"  🏴 {country}")


def main():
    """Main CLI entry point."""
    # Argument parsing
    # Command routing
    # Thin wrappers
```

**Result:**
- Pure CLI interface
- Thin wrapper functions
- All business logic delegated to other modules

### 4. Updated `run_multiple.py`

**Removed:**
- `discover_configs()` → Now imported from `discovery.py`
- `group_by_newspaper()` → Now imported from `discovery.py`

**Added:**
```python
from text.scrapers.orchestration.discovery import discover_configs, group_by_newspaper
```

**Result:**
- No code duplication
- Cleaner imports
- Reduced file size (~80 lines removed)

## File Organization

### Before Refactoring
```
src/text/scrapers/orchestration/
├── main.py              (293 lines) - CLI + utilities + discovery
├── run_scraper.py       (358 lines) - Single scraper execution
└── run_multiple.py      (512 lines) - Multi-scraper + discovery
```

### After Refactoring
```
src/text/scrapers/orchestration/
├── main.py              (210 lines) - CLI interface only
├── utils.py             (95 lines)  - Utilities (NEW)
├── discovery.py         (139 lines) - Discovery logic (NEW)
├── run_scraper.py       (358 lines) - Single scraper execution
└── run_multiple.py      (445 lines) - Multi-scraper orchestration
```

## Module Responsibilities

### `main.py` - CLI Interface
**Responsibilities:**
- Parse command-line arguments
- Route commands to appropriate modules
- Display formatted output to user
- Handle user interaction

**Does NOT:**
- Contain business logic
- Manage paths directly
- Discover configurations
- Set up logging (delegates to utils)

### `utils.py` - Utilities
**Responsibilities:**
- Logging configuration
- Path management
- Python path setup
- Common utilities

**Reusable by:**
- All orchestration modules
- External scripts
- Test suites

### `discovery.py` - Configuration Discovery
**Responsibilities:**
- Find YAML configuration files
- Organize configs by country/newspaper
- Group multi-country newspapers
- List available scrapers/countries

**Returns data, not formatted output:**
- Functions return structured data (dicts, lists)
- Presentation handled by CLI wrappers
- Easy to test and reuse

### `run_scraper.py` - Single Scraper Execution
**Responsibilities:**
- Execute single newspaper scraper
- Find scraper by name
- Run sequential groups
- Handle scraper lifecycle

**No changes needed** - Already well-organized

### `run_multiple.py` - Multi-Scraper Orchestration
**Responsibilities:**
- Launch parallel processes
- Monitor running scrapers
- Parse log files
- Summarize results
- Handle sequential groups

**Now imports from `discovery.py`:**
- No duplicate discovery code
- Cleaner organization

## Benefits

### 1. Separation of Concerns
- **main.py**: Pure CLI interface
- **utils.py**: Reusable utilities
- **discovery.py**: Business logic
- **run_scraper.py**: Execution logic
- **run_multiple.py**: Orchestration logic

### 2. Code Reusability
- Discovery functions can be used by other modules
- Utilities available across all code
- No duplication between modules

### 3. Testability
- Discovery functions return data (easy to test)
- CLI wrappers are thin (minimal testing needed)
- Clear function boundaries

### 4. Maintainability
- Each module has single, clear purpose
- Easy to locate specific functionality
- Reduced file sizes
- Clear import structure

### 5. Extensibility
- Easy to add new discovery functions
- Simple to create new utilities
- CLI can be extended without touching business logic

## Import Graph

```
main.py
├── imports utils (setup_logging, get_project_paths, get_default_configs_dir)
├── imports discovery (get_available_scrapers, get_available_countries)
├── imports run_scraper (run_scraper_by_name)
└── imports run_multiple (run_all_scrapers)

run_multiple.py
└── imports discovery (discover_configs, group_by_newspaper)

run_scraper.py
└── (no changes)

discovery.py
└── (no dependencies on other orchestration modules)

utils.py
└── (no dependencies on other orchestration modules)
```

## Backward Compatibility

### ✅ Fully Maintained

All existing commands work exactly as before:

```bash
# Single scraper
python src/text/scrapers/orchestration/main.py sibc
python src/text/scrapers/orchestration/main.py sibc --update

# Multi-scraper runner
python src/text/scrapers/orchestration/main.py --run-all
python src/text/scrapers/orchestration/main.py --run-all --sequential
python src/text/scrapers/orchestration/main.py --run-all --dry-run

# List commands
python src/text/scrapers/orchestration/main.py --list-scrapers
python src/text/scrapers/orchestration/main.py --list-countries
```

### New Capabilities

Can now import and use discovery functions programmatically:

```python
from text.scrapers.orchestration.discovery import get_available_scrapers

# Get all scrapers
scrapers = get_available_scrapers(configs_dir)

# Use in custom scripts, web APIs, etc.
for country, newspapers in scrapers.items():
    print(f"{country}: {newspapers}")
```

## Testing

### Unit Tests Can Now Test:

1. **Discovery Functions:**
```python
def test_discover_configs():
    configs = discover_configs(test_configs_dir)
    assert len(configs) == expected_count

def test_get_available_scrapers():
    scrapers = get_available_scrapers(test_configs_dir)
    assert "solomon_islands" in scrapers
    assert "sibc" in scrapers["solomon_islands"]
```

2. **Utility Functions:**
```python
def test_get_project_paths():
    paths = get_project_paths()
    assert "project_root" in paths
    assert paths["project_root"].exists()
```

3. **CLI Wrappers:**
```python
def test_list_scrapers_output(capsys):
    list_available_scrapers()
    captured = capsys.readouterr()
    assert "Available Newspaper Scrapers" in captured.out
```

## Code Quality Improvements

### Before
- Mixed responsibilities in `main.py`
- Duplicate code in `run_multiple.py`
- Hard to test business logic
- Unclear module boundaries

### After
- Clear separation of concerns
- No code duplication
- Easy to test all functions
- Well-defined module responsibilities

## Lines of Code

### Summary
- **main.py**: 293 → 210 lines (-83 lines, -28%)
- **run_multiple.py**: 512 → 445 lines (-67 lines, -13%)
- **utils.py**: 0 → 95 lines (NEW)
- **discovery.py**: 0 → 139 lines (NEW)
- **Total**: 805 → 889 lines (+84 lines, +10%)

**Note:** Total lines increased slightly, but code is now:
- Better organized
- More reusable
- Easier to test
- Clearer responsibilities

The small increase in total lines is offset by significant improvements in code quality and maintainability.

## Future Enhancements

With this refactoring, it's now easier to:

1. **Add new CLI commands** - Just modify `main.py`
2. **Create web API** - Import discovery functions directly
3. **Build monitoring dashboard** - Use discovery to list all scrapers
4. **Add unit tests** - Test each module independently
5. **Create custom scripts** - Reuse utilities and discovery functions

## Conclusion

The refactoring successfully:
- ✅ Moved all non-CLI code out of `main.py`
- ✅ Created reusable utility module
- ✅ Created dedicated discovery module
- ✅ Eliminated code duplication
- ✅ Improved testability
- ✅ Maintained full backward compatibility
- ✅ Enhanced code organization

The orchestration system is now cleaner, more maintainable, and better organized.
