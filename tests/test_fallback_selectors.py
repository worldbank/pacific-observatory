#!/usr/bin/env python3
"""
Test script to verify the fallback selector functionality.
"""

import sys
import os
from bs4 import BeautifulSoup

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from text.scrapers.parser import extract_article_data_from_soup

def test_fallback_selectors():
    """Test the fallback selector logic with different HTML structures."""
    
    # Test HTML with different article structures
    test_cases = [
        {
            "name": "Primary selector works",
            "html": """
            <html>
                <body>
                    <div class="entry-content">
                        <p>This is the main article content that should be extracted.</p>
                        <p>It has multiple paragraphs with good content.</p>
                    </div>
                </body>
            </html>
            """,
            "selectors": {
                "article_body": [".entry-content", ".post-content", ".article-body"]
            },
            "expected_content": "This is the main article content that should be extracted. It has multiple paragraphs with good content."
        },
        {
            "name": "Primary fails, fallback works",
            "html": """
            <html>
                <body>
                    <div class="post-content">
                        <p>This content is in a different container structure.</p>
                        <p>The primary selector won't find this, but the fallback will.</p>
                    </div>
                </body>
            </html>
            """,
            "selectors": {
                "article_body": [".entry-content", ".post-content", ".article-body"]
            },
            "expected_content": "This content is in a different container structure. The primary selector won't find this, but the fallback will."
        },
        {
            "name": "Multiple fallbacks needed",
            "html": """
            <html>
                <body>
                    <div class="article-body">
                        <p>This is in the third fallback selector.</p>
                        <p>Both primary and first fallback will fail.</p>
                    </div>
                </body>
            </html>
            """,
            "selectors": {
                "article_body": [".entry-content", ".post-content", ".article-body"]
            },
            "expected_content": "This is in the third fallback selector. Both primary and first fallback will fail."
        },
        {
            "name": "Single selector (backward compatibility)",
            "html": """
            <html>
                <body>
                    <div class="entry-content">
                        <p>Testing backward compatibility with single selector string.</p>
                        <p>This should work exactly as before.</p>
                    </div>
                </body>
            </html>
            """,
            "selectors": {
                "article_body": ".entry-content"
            },
            "expected_content": "Testing backward compatibility with single selector string. This should work exactly as before."
        },
        {
            "name": "No selectors work",
            "html": """
            <html>
                <body>
                    <div class="some-other-class">
                        <p>This content won't be found by any of our selectors.</p>
                    </div>
                </body>
            </html>
            """,
            "selectors": {
                "article_body": [".entry-content", ".post-content", ".article-body"]
            },
            "expected_content": None  # Should return empty string
        }
    ]
    
    print("Testing fallback selector functionality...")
    print("=" * 60)
    
    passed = 0
    failed = 0
    
    for test_case in test_cases:
        print(f"\nTest: {test_case['name']}")
        print("-" * 40)
        
        try:
            # Parse HTML
            soup = BeautifulSoup(test_case['html'], 'html.parser')
            
            # Extract content using the parser function
            result = extract_article_data_from_soup(
                soup, 
                f"test-url-{test_case['name'].replace(' ', '-')}", 
                test_case['selectors'], 
                "https://example.com"
            )
            
            # Get the body content
            body_content = result.get('body', '')
            
            # Check result
            if test_case['expected_content'] is None:
                # Expecting no content found
                if not body_content:
                    print(f"✅ PASS: No content found as expected")
                    passed += 1
                else:
                    print(f"❌ FAIL: Expected no content but got: '{body_content[:50]}...'")
                    failed += 1
            else:
                # Expecting content to be found
                expected = test_case['expected_content']
                if body_content and body_content.strip() == expected:
                    print(f"✅ PASS: Content extracted successfully")
                    print(f"   Content: '{body_content[:100]}...'")
                    passed += 1
                else:
                    print(f"❌ FAIL: Expected '{expected}' but got: '{body_content}'")
                    failed += 1
                    
        except Exception as e:
            print(f"💥 ERROR: {e}")
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All tests passed! Fallback selector logic is working correctly.")
    else:
        print(f"⚠️  {failed} tests failed. Please review the implementation.")
    
    return failed == 0

if __name__ == "__main__":
    success = test_fallback_selectors()
    sys.exit(0 if success else 1)
