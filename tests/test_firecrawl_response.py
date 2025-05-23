"""
Test to understand the ScrapeResponse object structure
"""

import os
from dotenv import load_dotenv
from firecrawl import FirecrawlApp

load_dotenv()

def test_scrape_response():
    """Test to understand ScrapeResponse object"""
    api_key = os.getenv("FIRECRAWL_API_KEY")
    if not api_key:
        print("❌ No API key found")
        return
    
    firecrawl = FirecrawlApp(api_key=api_key)
    test_url = "https://example.com"
    
    print("🧪 Testing ScrapeResponse object structure...")
    try:
        # Test with the working format (keyword arguments)
        result = firecrawl.scrape_url(
            test_url,
            onlyMainContent=True,
            formats=['markdown']
        )
        
        print(f"✅ API call successful!")
        print(f"📋 Result type: {type(result)}")
        print(f"📋 Result attributes: {dir(result)}")
        
        # Try common attributes
        if hasattr(result, 'data'):
            print(f"📄 result.data: {type(result.data)}")
            if hasattr(result.data, 'keys'):
                print(f"📄 result.data keys: {list(result.data.keys())}")
        
        if hasattr(result, 'markdown'):
            print(f"📄 result.markdown length: {len(result.markdown)}")
            
        if hasattr(result, 'content'):
            print(f"📄 result.content length: {len(result.content)}")
            
        if hasattr(result, 'metadata'):
            print(f"📄 result.metadata: {result.metadata}")
            
        # Try to access as dictionary methods
        try:
            # Check if it's dict-like
            if 'markdown' in result:
                print(f"📄 Contains markdown key")
        except Exception as e:
            print(f"📄 Not dict-like: {e}")
            
        return result
        
    except Exception as e:
        print(f"❌ Failed: {e}")
        return None

if __name__ == "__main__":
    result = test_scrape_response()
    if result:
        print(f"\n📊 Final result: {result}")
