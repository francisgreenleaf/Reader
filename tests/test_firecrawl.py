import os
from dotenv import load_dotenv
from firecrawl import FirecrawlApp

# Load environment variables
load_dotenv()

api_key = os.getenv('FIRECRAWL_API_KEY')
print(f"API Key: {api_key}")
print(f"API Key length: {len(api_key) if api_key else 'None'}")

try:
    # Initialize FirecrawlApp
    app = FirecrawlApp(api_key=api_key)
    print("✓ FirecrawlApp initialized successfully")
    
    # Test with a simple URL
    result = app.scrape_url('https://example.com', params={'formats': ['markdown']})
    print("✓ Successfully scraped URL")
    print(f"Result keys: {result.keys() if isinstance(result, dict) else 'Not a dict'}")
    
    if isinstance(result, dict):
        title = result.get('title', 'No title')
        content_length = len(result.get('markdown', ''))
        print(f"Title: {title}")
        print(f"Content length: {content_length}")
    
except Exception as e:
    print(f"✗ Error: {e}")
    print(f"Error type: {type(e)}")
