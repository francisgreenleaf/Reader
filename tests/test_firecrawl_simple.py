"""
Simple Firecrawl API test to determine correct format
"""

import os
from dotenv import load_dotenv
from firecrawl import FirecrawlApp

load_dotenv()

def test_firecrawl_formats():
    """Test different ways to call the Firecrawl API"""
    api_key = os.getenv("FIRECRAWL_API_KEY")
    if not api_key:
        print("❌ No API key found")
        return
    
    firecrawl = FirecrawlApp(api_key=api_key)
    test_url = "https://example.com"
    
    # Test 1: Direct parameters (new v1 format)
    print("🧪 Test 1: Direct parameters as keyword arguments")
    try:
        result = firecrawl.scrape_url(
            test_url,
            onlyMainContent=True,
            formats=['markdown']
        )
        print(f"✅ Success! Content length: {len(result.get('markdown', ''))}")
        return result
    except Exception as e:
        print(f"❌ Failed: {e}")
    
    # Test 2: Single dictionary parameter
    print("\n🧪 Test 2: Single dictionary parameter")
    try:
        result = firecrawl.scrape_url(test_url, {
            'onlyMainContent': True,
            'formats': ['markdown']
        })
        print(f"✅ Success! Content length: {len(result.get('markdown', ''))}")
        return result
    except Exception as e:
        print(f"❌ Failed: {e}")
    
    # Test 3: No additional parameters
    print("\n🧪 Test 3: No additional parameters (defaults)")
    try:
        result = firecrawl.scrape_url(test_url)
        print(f"✅ Success! Keys in result: {list(result.keys()) if result else 'None'}")
        return result
    except Exception as e:
        print(f"❌ Failed: {e}")
    
    print("\n❌ All tests failed. The API format may have changed significantly.")
    return None

if __name__ == "__main__":
    test_firecrawl_formats()
