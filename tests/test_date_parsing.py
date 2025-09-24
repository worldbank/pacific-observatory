#!/usr/bin/env python3
"""
Test script to verify the enhanced date parsing functionality.
This tests the specific case that was failing: "- September 24, 2025"
"""

import sys
import os

# Add the src directory to the path so we can import the cleaning module
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from text.scrapers.pipelines.cleaning import handle_mixed_dates

def test_date_parsing():
    """Test various date formats including the problematic case."""
    
    test_cases = [
        # The original problematic case
        ("- September 24, 2025", "2025-09-24"),
        
        # Other prefix/suffix cases
        ("• September 24, 2025", "2025-09-24"),
        ("* September 24, 2025", "2025-09-24"),
        ("| September 24, 2025", "2025-09-24"),
        ("Published: September 24, 2025", "2025-09-24"),
        ("Date: September 24, 2025", "2025-09-24"),
        ("On September 24, 2025", "2025-09-24"),
        
        # Standard formats that should still work
        ("September 24, 2025", "2025-09-24"),
        ("Sep 24, 2025", "2025-09-24"),
        ("24 September 2025", "2025-09-24"),
        ("2025-09-24", "2025-09-24"),
        ("09/24/2025", "2025-09-24"),
        ("24/09/2025", "2025-09-24"),
        
        # Edge cases with extra text
        ("By John Doe - September 24, 2025", "2025-09-24"),
        ("Updated: September 24, 2025 14:30", "2025-09-24"),
        ("Monday, September 24, 2025", "2025-09-24"),
        
        # HTML entities
        ("&ndash; September 24, 2025", "2025-09-24"),
        
        # Multiple spaces/formatting
        ("  -   September   24,   2025  ", "2025-09-24"),
    ]
    
    print("Testing enhanced date parsing functionality...")
    print("=" * 60)
    
    passed = 0
    failed = 0
    
    for input_date, expected_output in test_cases:
        try:
            result = handle_mixed_dates(input_date)
            if result == expected_output:
                print(f"✅ PASS: '{input_date}' -> '{result}'")
                passed += 1
            else:
                print(f"❌ FAIL: '{input_date}' -> '{result}' (expected '{expected_output}')")
                failed += 1
        except Exception as e:
            print(f"💥 ERROR: '{input_date}' -> Exception: {e}")
            failed += 1
    
    print("=" * 60)
    print(f"Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All tests passed! The enhanced date parsing is working correctly.")
    else:
        print(f"⚠️  {failed} tests failed. Please review the implementation.")
    
    return failed == 0

if __name__ == "__main__":
    success = test_date_parsing()
    sys.exit(0 if success else 1)
