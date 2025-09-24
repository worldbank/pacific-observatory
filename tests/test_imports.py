#!/usr/bin/env python3
"""
Test script to verify imports work correctly.
"""

import sys
from pathlib import Path

# Add the src directory to Python path for imports
project_root = Path(__file__).parent
src_dir = project_root / "src"
sys.path.insert(0, str(src_dir))

try:
    print("Testing imports...")
    
    # Test basic imports
    from src.text.scrapers.factory import find_config_files
    print("✅ Factory import successful")
    
    from src.text.scrapers.orchestration.run_scraper import run_single_scraper
    print("✅ Orchestration import successful")
    
    from src.text.scrapers.models import NewspaperConfig, ThumbnailRecord, ArticleRecord
    print("✅ Models import successful")
    
    # Test model creation
    thumbnail_data = {
        "url": "https://example.com/article",
        "title": "Test Article",
        "date": "2025-01-01"
    }
    thumbnail = ThumbnailRecord(**thumbnail_data)
    print("✅ ThumbnailRecord creation successful")
    
    article_data = {
        "url": "https://example.com/article",
        "title": "Test Article", 
        "date": "2025-01-01",
        "body": "Test article content",
        "tags": ["test", "article"],
        "source": "Test Source",
        "country": "US"
    }
    article = ArticleRecord(**article_data)
    print("✅ ArticleRecord creation successful")
    
    # Test config discovery
    scrapers_dir = src_dir / "text" / "scrapers"
    configs_dir = scrapers_dir / "configs"
    
    if configs_dir.exists():
        config_files = find_config_files(configs_dir)
        print(f"✅ Found {len(config_files)} configuration files")
        
        for config_file in config_files:
            rel_path = config_file.relative_to(configs_dir)
            print(f"   📄 {rel_path}")
    else:
        print("⚠️  Configs directory not found")
    
    print("\n🎉 All imports successful! The main script should work.")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)
