# Text Scrapers Framework

This directory contains the core components of the Pacific Observatory's **config-driven newspaper scraping system**. The framework is designed to scrape news articles from multiple newspapers across different countries using a modular, scalable architecture.

## 🏗️ Architecture Overview

The system follows a **two-phase scraping process**:
1. **Listing Discovery** → Find article thumbnails (URLs, titles, dates) from archive/pagination pages
2. **Article Extraction** → Retrieve full article content (body, tags, metadata)

All site-specific configuration is externalized to YAML files, allowing new newspapers to be added without writing Python code.

## 📁 Core Components

### Client Layer
- **`client_http.py`** - High-performance async HTTP client using `httpx` and `asyncio` for static content scraping with configurable concurrency and rate limiting
- **`client_browser.py`** - Selenium-based browser client for dynamic JavaScript-rendered sites with cookie management and CDP support

### Data & Configuration
- **`models.py`** - Pydantic data models (`ThumbnailRecord`, `ArticleRecord`, `NewspaperConfig`) providing strict validation and type safety
- **`configs/`** - YAML configuration files organized by country, defining selectors, pagination strategies, and site-specific settings

### Scraping Logic
- **`newspaper_scraper.py`** - Main orchestrator class that coordinates listing discovery, article extraction, data validation, and file storage
- **`listing_strategies.py`** - Pluggable strategies for discovering article URLs (pagination, archive, category, search) with dynamic page detection
- **`factory.py`** - Factory functions for creating scraper instances from YAML configurations

### Pipeline Components
- **`pipelines/`** - Data processing modules:
  - `storage.py` - JSONL file storage with organized directory structure
  - `cleaning.py` - Site-specific data cleaning functions

### Orchestration
- **`orchestration/`** - Entry point scripts:
  - `run_scraper.py` - Run single newspaper scraper
  - `main.py` - Batch processing and coordination

### Utilities
- **`utils.py`** - Shared utility functions for cookie management, URL handling, and common operations

## 🚀 Key Features

### Performance & Scalability
- **Asynchronous HTTP** - Concurrent request processing with configurable limits (10-150 concurrent requests)
- **Rate Limiting** - Configurable delays (0.01-0.5s) to respect server capacity
- **Batch Processing** - Memory-efficient handling of large URL lists
- **Dynamic Pagination** - Automatic discovery of all available pages without hardcoded limits

### Configuration-Driven
- **YAML Configs** - All site-specific logic externalized to configuration files
- **Multiple Strategies** - Support for pagination, archive, category, and search-based listing discovery
- **Custom Headers** - Configurable HTTP headers for anti-bot compatibility
- **Cookie Management** - File-based session persistence with auto-save/load capabilities

### Data Quality
- **Pydantic Validation** - Strict schema enforcement for all extracted data
- **Custom Cleaning** - Site-specific data normalization functions
- **Error Handling** - Graceful failure handling with detailed logging
- **JSONL Output** - Structured, validated data storage

### Authentication & Compatibility
- **Cookie Support** - Persistent session management for protected sites
- **Browser Automation** - Selenium fallback for JavaScript-heavy sites
- **Header Customization** - User-Agent rotation and custom headers
- **Cloudflare Handling** - Support for protected sites requiring browser sessions

## 📊 Data Flow

```
YAML Config → Factory → NewspaperScraper → Listing Strategy → HTTP/Browser Client
     ↓                                                              ↓
Storage ← Pydantic Models ← Data Cleaning ← Article Extraction ← Raw HTML
```

## 🔧 Configuration Example

```yaml
name: "Example News"
country: "XX"
base_url: "https://example.com"
client: "http"
concurrency: 10
rate_limit: 0.1

listing:
  type: "pagination"
  url_template: "https://example.com/news/page/{num}"
  batch_size: 50

selectors:
  thumbnail: ".article-card"
  title: "h2 a::text"
  url: "h2 a::attr(href)"
  date: ".date::text"
  article_body: ".content p"

cleaning:
  date: "clean_example_date"
```

This framework enables rapid deployment of scrapers for new newspapers while maintaining high performance, data quality, and maintainability standards.
