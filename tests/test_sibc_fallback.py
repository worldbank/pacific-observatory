#!/usr/bin/env python3
"""
Simple test to verify SIBC fallback selector functionality.
"""

import sys
import os
from pathlib import Path
from bs4 import BeautifulSoup

# Add the src directory to the path
project_root = Path(__file__).parent
src_dir = project_root / "src"
sys.path.insert(0, str(src_dir))

from text.scrapers.parser import extract_article_data_from_soup

def test_sibc_fallback():
    """Test SIBC fallback selectors with realistic HTML."""
    
    # Test HTML that matches SIBC structure
    test_html = """
    <html>
        <body>
            <article>
                <div class="entry-body">
                    <div>
                        <p>This is the main article content from SIBC.</p>
                        <p>It should be extracted by the fallback selector.</p>
                        <p>The primary selector .entry-body p won't work because these are nested in divs.</p>
                    </div>
                </div>
            </article>
        </body>
    </html>
    """
    
    # SIBC selectors from config
    selectors = {
        "article_body": [
            ".entry-body p",
            "article div.entry-body div"
        ]
    }
    
    print("Testing SIBC fallback selector functionality...")
    print("=" * 60)
    
    try:
        # Parse HTML
        soup = BeautifulSoup(test_html, 'html.parser')
        
        # Extract content using the parser function
        result = extract_article_data_from_soup(
            soup, 
            "https://www.sibconline.com.sb/test-article", 
            selectors, 
            "https://www.sibconline.com.sb"
        )
        
        # Get the body content
        body_content = result.get('body', '')
        
        print(f"Extracted content: '{body_content}'")
        
        expected_content = "This is the main article content from SIBC. It should be extracted by the fallback selector. The primary selector .entry-body p won't work because these are nested in divs."
        
        if body_content and body_content.strip() == expected_content:
            print("✅ SUCCESS: Fallback selector worked correctly!")
            print("   Primary selector failed as expected")
            print("   Fallback selector extracted the content successfully")
            return True
        else:
            print("❌ FAILURE: Fallback selector didn't work as expected")
            print(f"   Expected: '{expected_content}'")
            print(f"   Got: '{body_content}'")
            return False
            
    except Exception as e:
        print(f"💥 ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_sibc_fallback()
    sys.exit(0 if success else 1)
