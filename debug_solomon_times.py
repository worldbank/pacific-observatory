#!/usr/bin/env python3
"""
Debug script to inspect Solomon Times HTML structure.
"""

import asyncio
import httpx
from bs4 import BeautifulSoup

async def debug_solomon_times():
    """Debug Solomon Times HTML structure."""
    
    # Test a recent archive URL
    test_url = "https://www.solomontimes.com/news/latest/2023/12"
    
    print(f"🔍 Inspecting Solomon Times HTML structure")
    print(f"URL: {test_url}")
    print("=" * 60)
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9"
    }
    
    try:
        async with httpx.AsyncClient(headers=headers, timeout=30.0) as client:
            response = await client.get(test_url)
            
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Look for potential article containers
                print("\n🔍 Looking for article containers...")
                
                # Test various selectors that might contain articles
                selectors_to_test = [
                    ".article-list-item",
                    ".article-item", 
                    ".post",
                    ".entry",
                    ".news-item",
                    "article",
                    ".content-item",
                    "[class*='article']",
                    "[class*='post']",
                    "[class*='news']"
                ]
                
                for selector in selectors_to_test:
                    elements = soup.select(selector)
                    if elements:
                        print(f"✅ Found {len(elements)} elements with selector: {selector}")
                        
                        # Show first element structure
                        if elements:
                            first_elem = elements[0]
                            print(f"   First element HTML (truncated):")
                            elem_html = str(first_elem)[:500]
                            print(f"   {elem_html}...")
                            
                            # Look for links and titles within
                            links = first_elem.find_all('a')
                            if links:
                                print(f"   Contains {len(links)} links")
                                for i, link in enumerate(links[:3]):  # Show first 3 links
                                    href = link.get('href', 'No href')
                                    text = link.get_text(strip=True)[:100]
                                    print(f"     Link {i+1}: {href} -> '{text}'")
                            
                            # Look for headings
                            headings = first_elem.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
                            if headings:
                                print(f"   Contains {len(headings)} headings")
                                for i, heading in enumerate(headings[:3]):
                                    text = heading.get_text(strip=True)[:100]
                                    print(f"     {heading.name}: '{text}'")
                        
                        print()
                    else:
                        print(f"❌ No elements found with selector: {selector}")
                
                # Also check the page title and overall structure
                title = soup.find('title')
                if title:
                    print(f"📄 Page title: {title.get_text(strip=True)}")
                
                # Look for any elements that might contain dates
                print("\n🗓️ Looking for date elements...")
                date_selectors = [
                    ".date",
                    ".timestamp", 
                    ".published",
                    "[class*='date']",
                    "[class*='time']"
                ]
                
                for selector in date_selectors:
                    elements = soup.select(selector)
                    if elements:
                        print(f"✅ Found {len(elements)} date elements with selector: {selector}")
                        for i, elem in enumerate(elements[:3]):
                            text = elem.get_text(strip=True)
                            print(f"   Date {i+1}: '{text}'")
                
            else:
                print(f"❌ Failed to fetch page: HTTP {response.status_code}")
                print(f"Response text (first 500 chars): {response.text[:500]}")
                
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_solomon_times())
