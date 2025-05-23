import requests
import time
import json

def test_fetch_endpoint_rate_limit():
    """
    Test the rate limiting on the /fetch endpoint
    The endpoint is limited to 30 requests per minute
    """
    url = "http://localhost:8080/fetch"
    headers = {"Content-Type": "application/json"}
    data = {"url": "https://example.com"}
    
    print("Testing /fetch endpoint rate limit (30 per minute)...")
    
    # Make 35 requests (more than the 30 per minute limit)
    for i in range(35):
        response = requests.post(url, headers=headers, data=json.dumps(data))
        status_code = response.status_code
        
        if status_code == 429:  # 429 is the status code for "Too Many Requests"
            print(f"Request {i+1}: Rate limit hit! Status code: {status_code}")
            print(f"Response: {response.text}")
            print(f"Rate limiting is working correctly after {i+1} requests.")
            return True
        else:
            print(f"Request {i+1}: Status code: {status_code}")
        
        # Small delay to avoid overwhelming the server
        time.sleep(0.1)
    
    print("Completed 35 requests without hitting rate limit. Rate limiting may not be working.")
    return False

def test_generate_pdf_endpoint_rate_limit():
    """
    Test the rate limiting on the /generate_pdf endpoint
    The endpoint is limited to 10 requests per minute
    """
    url = "http://localhost:8080/generate_pdf"
    headers = {"Content-Type": "application/json"}
    data = {
        "title": "Test Article",
        "content": "This is a test article content for rate limiting test.",
        "imageUrl": ""
    }
    
    print("\nTesting /generate_pdf endpoint rate limit (10 per minute)...")
    
    # Make 15 requests (more than the 10 per minute limit)
    for i in range(15):
        response = requests.post(url, headers=headers, data=json.dumps(data))
        status_code = response.status_code
        
        if status_code == 429:  # 429 is the status code for "Too Many Requests"
            print(f"Request {i+1}: Rate limit hit! Status code: {status_code}")
            print(f"Response: {response.text}")
            print(f"Rate limiting is working correctly after {i+1} requests.")
            return True
        else:
            print(f"Request {i+1}: Status code: {status_code}")
        
        # Small delay to avoid overwhelming the server
        time.sleep(0.1)
    
    print("Completed 15 requests without hitting rate limit. Rate limiting may not be working.")
    return False

def test_query_endpoint_rate_limit():
    """
    Test the rate limiting on the /query endpoint
    The endpoint is limited to 20 requests per minute
    """
    url = "http://localhost:8080/query"
    headers = {"Content-Type": "application/json"}
    data = {
        "model": "gpt-3.5-turbo",
        "content": "This is test content for the article.",
        "query": "What is this article about?"
    }
    
    print("\nTesting /query endpoint rate limit (20 per minute)...")
    
    # Make 25 requests (more than the 20 per minute limit)
    for i in range(25):
        response = requests.post(url, headers=headers, data=json.dumps(data))
        status_code = response.status_code
        
        if status_code == 429:  # 429 is the status code for "Too Many Requests"
            print(f"Request {i+1}: Rate limit hit! Status code: {status_code}")
            print(f"Response: {response.text}")
            print(f"Rate limiting is working correctly after {i+1} requests.")
            return True
        else:
            print(f"Request {i+1}: Status code: {status_code}")
        
        # Small delay to avoid overwhelming the server
        time.sleep(0.1)
    
    print("Completed 25 requests without hitting rate limit. Rate limiting may not be working.")
    return False

def check_tokenguard_implementation():
    """
    Check if TokenGuard is implemented in the application
    """
    print("\nChecking TokenGuard implementation...")
    
    # Examine app.py for TokenGuard usage
    with open("app.py", "r") as f:
        app_code = f.read()
    
    if "tokenguard" in app_code:
        if "# this is where tokenguard should be initialized - currently it is not being used" in app_code:
            print("TokenGuard is imported but not used in the application.")
            print("Comment in code indicates it should be initialized but isn't currently used.")
            return False
        else:
            print("TokenGuard appears to be imported and may be used in the application.")
            return True
    else:
        print("TokenGuard is not imported or used in the application.")
        return False

if __name__ == "__main__":
    print("Starting rate limiting tests...")
    print("Note: These tests require the Flask application to be running on localhost:8080")
    print("Make sure the application is running before proceeding.")
    
    input("Press Enter to start the tests...")
    
    # Test each endpoint's rate limiting
    fetch_result = test_fetch_endpoint_rate_limit()
    pdf_result = test_generate_pdf_endpoint_rate_limit()
    query_result = test_query_endpoint_rate_limit()
    
    # Check TokenGuard implementation
    tokenguard_result = check_tokenguard_implementation()
    
    # Summary of results
    print("\n=== Rate Limiting Test Results ===")
    print(f"Fetch endpoint (/fetch) rate limiting: {'Working' if fetch_result else 'Not working or not triggered'}")
    print(f"PDF generation endpoint (/generate_pdf) rate limiting: {'Working' if pdf_result else 'Not working or not triggered'}")
    print(f"Query endpoint (/query) rate limiting: {'Working' if query_result else 'Not working or not triggered'}")
    print(f"TokenGuard implementation: {'Implemented' if tokenguard_result else 'Not implemented'}")
    
    if fetch_result or pdf_result or query_result:
        print("\nConclusion: Rate limiting is working on at least one endpoint.")
    else:
        print("\nConclusion: Rate limiting does not appear to be working on any tested endpoint.")
    
    if not tokenguard_result:
        print("Note: TokenGuard is not currently being used in the application, even though the class exists.")
