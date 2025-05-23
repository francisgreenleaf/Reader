import os
import requests
from dotenv import load_dotenv
from firecrawl import FirecrawlApp

# Load environment variables
load_dotenv()

api_key = os.getenv('FIRECRAWL_API_KEY')
print(f"API Key: {api_key}")

# Initialize FirecrawlApp and check its configuration
app = FirecrawlApp(api_key=api_key)
print(f"API URL: {app.api_url}")
print(f"API Key in app: {app.api_key}")

# Let's try to make a direct request to see what happens
headers = {
    'Content-Type': 'application/json',
    'Authorization': f'Bearer {api_key}'
}

# Try the same URL that MCP uses
try:
    print("\n--- Direct API Request Test ---")
    url = f"{app.api_url}/v1/scrape"
    data = {
        "url": "https://example.com",
        "formats": ["markdown"]
    }
    
    print(f"Request URL: {url}")
    print(f"Headers: {headers}")
    print(f"Data: {data}")
    
    response = requests.post(url, json=data, headers=headers)
    print(f"Response status: {response.status_code}")
    print(f"Response text: {response.text[:500]}...")
    
except Exception as e:
    print(f"Direct request error: {e}")

# Also try other variations of the Authorization header
print("\n--- Testing different auth methods ---")
auth_variations = [
    f'Bearer {api_key}',
    f'Token {api_key}',
    api_key
]

for i, auth in enumerate(auth_variations):
    try:
        test_headers = {'Content-Type': 'application/json', 'Authorization': auth}
        response = requests.post(f"{app.api_url}/v1/scrape", json={"url": "https://example.com", "formats": ["markdown"]}, headers=test_headers)
        print(f"Variation {i+1} ({auth[:20]}...): Status {response.status_code}")
        if response.status_code != 401:
            print(f"SUCCESS with auth: {auth}")
            break
    except Exception as e:
        print(f"Variation {i+1} error: {e}")
