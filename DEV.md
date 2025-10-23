## Completed Changes

### JSONL to CSV Migration (Scrapers)

- [x] **Convert all data exports to CSV format** across `src/text/scrapers/pipelines/storage.py`
  - ✅ Renamed `JsonlStorage` → `CSVStorage`
  - ✅ `save_articles()`: Exports to `news.csv` with tags as comma-separated strings
  - ✅ `save_thumbnails_as_urls()`: Exports to `urls.csv`
  - ✅ `save_failed_urls()`: Exports to `failed/failed_urls_{YYYYMMDD}.csv`
  - ✅ `save_failed_news()`: Exports to `failed/failed_news_{YYYYMMDD}.csv`
  - ✅ `save_metadata()`: Preserved as JSON in `metadata/{type}_metadata_{timestamp}.json`
  - ✅ All exports use `index=False` and proper HttpUrl serialization

- [x] **CSV Reading Methods**
  - ✅ `load_existing_articles()`: Reads from `news.csv`, reconstructs ArticleRecord objects
  - ✅ `get_existing_article_urls()`: Efficient URL lookup for update mode

- [x] **Updated all references**
  - ✅ `src/text/scrapers/newspaper_scraper.py`: Updated imports and initialization
  - ✅ `src/text/scrapers/orchestration/run_scraper.py`: Updated imports
  - ✅ `src/text/scrapers/pipelines/__init__.py`: Updated exports
  - ✅ `src/text/scrapers/__init__.py`: Updated exports
  - ✅ `tests/test_scrapers.py`: Updated imports and test initialization

- [x] **Analysis module CSV reading**
  - ✅ `src/text/analysis/epu.py`: Updated `process_data()` to read CSV instead of JSONL
  - ✅ `src/text/analysis/main.py`: Updated `get_epu()` and `get_sentiment()` to read `*/news.csv`

### EPU additional_name Parameter

- [x] **Add additional_name parameter to EPU class**
  - ✅ Added `additional_name: Union[str, None] = None` parameter to constructor
  - ✅ Stored as `self.additional_name` instance variable
  - ✅ Validation: If `additional_name` is None, `additional_terms` must also be None
  - ✅ `calculate_epu_score()`: Creates column `epu_{additional_name}` with weighted EPU scores when provided

- [x] **Export logic with dynamic filenames**
  - ✅ If `additional_name` is None: exports to `{country_name}_epu.csv`
  - ✅ If `additional_name` provided: exports to `{country_name}_epu_{additional_name}.csv`
  - ✅ Example: `solomon_islands_epu_inflation.csv` for inflation-related EPU

- [x] **Updated main.py functions**
  - ✅ `get_epu()`: Added `additional_name` parameter, passes to EPU, uses for filename
  - ✅ `get_sentiment()`: Added `additional_name` parameter for consistency
  - ✅ Main block: Added `additional_name` variable (default None)
  - ✅ All CSV exports use `index=False`

## Remaining Tasks

- [ ] **Test additional_name functionality**
  - Test EPU generation with `additional_name` parameter
  - Verify correct filename generation: `epu_{additional_name}.csv`
  - Verify correct column naming: `epu_{additional_name}` with weighted scores
  - Test validation: Ensure `additional_name=None` requires `additional_terms=None`
  - Test with actual newspaper data (SIBC, Solomon Star)
  - Verify CSV output format and data integrity

## Future Developments

### 1. Country Expansion (12+ Additional Newspapers)

- [ ] **Identify and configure 12+ newspapers** from additional countries
  - Create YAML config files for each newspaper in appropriate country directories
  - Define CSS selectors, pagination strategies, and cleaning functions per newspaper
  - Test scraper on each configuration
  - Document country/newspaper mapping and any special handling requirements

- [ ] **Standardize newspaper configuration patterns**
  - Ensure consistent schema across all newspaper configs
  - Create template config file for new newspapers
  - Document selector discovery process and best practices


  I've included Antara and Jakarta Post scrapers.

  I need to create an Index Strategy for Tempo later:
  https://en.tempo.co/index/2025-10-23/

### 2. Online Shopping Scraper Structure

- [ ] **Design online shopping scraper architecture**
  - Create `src/shopping/` module parallel to `src/text/`
  - Define data models for shopping data (products, prices, categories, timestamps)
  - Implement shopping-specific cleaning and normalization functions
  - Design storage layer for shopping data (CSV format)

- [ ] **Implement core shopping scraper**
  - Create base scraper class for e-commerce platforms
  - Support multiple shopping platforms (e.g., local marketplaces, regional retailers)
  - Implement price tracking and historical data management
  - Add product deduplication and update detection

### 3. Fully Automated Scraping System

- [ ] **Storage and File Transfer Infrastructure**
  - **OneDrive Integration**:
    - Implement OneDrive API client for automated file uploads
    - Handle authentication and token refresh
    - Support incremental uploads and versioning
    - Requires: OneDrive API credentials and admin authorization
  
  - **GitHub Actions Automation**:
    - Create workflow files for scheduled scraping (daily/weekly)
    - Implement artifact storage for scraping results
    - Add notifications for scraping failures
    - Support both newspaper and shopping scrapers
    - Requires: GitHub Actions secrets for API keys and credentials
  
  - **GitHub Virtual Machines**:
    - Set up self-hosted runners for resource-intensive scraping
    - Configure environment with required dependencies
    - Implement job scheduling and monitoring
    - Handle data transfer from VMs to storage backends
    - Requires: GitHub organization admin access and VM provisioning

- [ ] **Credential and Secrets Management**
  - Centralize API keys, authentication tokens, and credentials
  - Use GitHub Secrets for CI/CD pipeline variables
  - Implement environment-based configuration (dev/staging/prod)
  - Document credential rotation procedures
  - **Note**: Requires admin authorization to manage organization-level secrets

- [ ] **Monitoring and Logging**
  - Implement centralized logging for all scrapers
  - Create dashboards for scraping health and statistics
  - Set up alerts for failures and anomalies
  - Track data quality metrics and validation results

- [ ] **Data Pipeline Orchestration**
  - Coordinate newspaper and shopping scraper runs
  - Implement dependency management between scrapers
  - Handle data aggregation and analysis workflows
  - Support incremental updates and full refreshes

### Implementation Priority

1. **Phase 1**: Country expansion (newspapers) - leverage existing infrastructure
2. **Phase 2**: Online shopping scraper structure - parallel to newspaper system
3. **Phase 3**: GitHub Actions automation - basic scheduled runs
4. **Phase 4**: OneDrive integration - centralized storage
5. **Phase 5**: Self-hosted runners - for resource-intensive operations

### Admin Authorization Required

- GitHub organization secrets and variables
- OneDrive API application registration and permissions
- Self-hosted runner configuration and management
- Credential rotation and security policies