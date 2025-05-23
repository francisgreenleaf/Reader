"""
Test script to verify that the query validation system works correctly
"""

import os
import requests
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_query_validation():
    """Test the query validation functionality"""
    print("🧪 Testing Query Validation System...")
    print("=" * 50)
    
    # Sample content for testing
    test_content = """
    # Artificial Intelligence in Healthcare
    
    Artificial Intelligence (AI) is revolutionizing healthcare by enabling more accurate 
    diagnoses, personalized treatment plans, and improved patient outcomes. Machine learning 
    algorithms can analyze medical imaging data to detect diseases like cancer earlier than 
    traditional methods.
    
    AI-powered diagnostic tools are being used in radiology to identify abnormalities in 
    X-rays, MRIs, and CT scans. These systems can process thousands of images quickly and 
    flag potential issues for radiologists to review.
    
    Drug discovery is another area where AI is making significant impact. By analyzing 
    molecular structures and predicting drug interactions, AI can accelerate the development 
    of new medications and reduce costs.
    """
    
    test_title = "Artificial Intelligence in Healthcare"
    
    # Test queries - mix of relevant and irrelevant
    test_queries = [
        # Valid queries (should pass validation)
        {
            "query": "How is AI being used in medical imaging?",
            "should_pass": True,
            "description": "Direct question about article content"
        },
        {
            "query": "What are the benefits of AI in healthcare?",
            "should_pass": True,
            "description": "General question about article topic"
        },
        {
            "query": "How does machine learning help with cancer detection?",
            "should_pass": True,
            "description": "Specific question about mentioned use case"
        },
        
        # Invalid queries (should be blocked)
        {
            "query": "What's the weather like today?",
            "should_pass": False,
            "description": "Weather query (completely unrelated)"
        },
        {
            "query": "How do I bake a chocolate cake?",
            "should_pass": False,
            "description": "Cooking/recipe query"
        },
        {
            "query": "Hello, how are you?",
            "should_pass": False,
            "description": "Greeting/chat query"
        },
        {
            "query": "What is 2+2?",
            "should_pass": False,
            "description": "Math calculation unrelated to content"
        },
        {
            "query": "Hi",
            "should_pass": False,
            "description": "Too short/vague query"
        },
        
        # Edge cases
        {
            "query": "Tell me about healthcare technology trends",
            "should_pass": True,
            "description": "Related but broader topic"
        },
        {
            "query": "What are the latest news about AI?",
            "should_pass": False,
            "description": "Current events query (may be flagged)"
        }
    ]
    
    # Test endpoint URL
    base_url = "http://localhost:8080"
    
    # Test results
    results = {
        "passed": 0,
        "failed": 0,
        "errors": []
    }
    
    print(f"Testing {len(test_queries)} queries...")
    print()
    
    for i, test_case in enumerate(test_queries, 1):
        query = test_case["query"]
        should_pass = test_case["should_pass"]
        description = test_case["description"]
        
        print(f"Test {i}: {description}")
        print(f"Query: '{query}'")
        print(f"Expected: {'PASS' if should_pass else 'BLOCK'}")
        
        try:
            # Send query request
            response = requests.post(f"{base_url}/query", json={
                "model": "gpt-4o-mini",
                "content": test_content,
                "query": query,
                "title": test_title
            })
            
            if should_pass:
                # Query should succeed (status 200)
                if response.status_code == 200:
                    print("✅ PASS - Query was accepted (as expected)")
                    results["passed"] += 1
                elif response.status_code == 422:
                    print("❌ FAIL - Query was blocked (unexpected)")
                    results["failed"] += 1
                    results["errors"].append(f"Test {i}: Expected acceptance but got blocked")
                else:
                    print(f"⚠️  UNEXPECTED - Status code: {response.status_code}")
                    results["errors"].append(f"Test {i}: Unexpected status {response.status_code}")
            else:
                # Query should be blocked (status 422)
                if response.status_code == 422:
                    print("✅ PASS - Query was blocked (as expected)")
                    response_data = response.json()
                    if 'suggestions' in response_data and response_data['suggestions']:
                        print(f"   Suggestions provided: {len(response_data['suggestions'])}")
                    results["passed"] += 1
                elif response.status_code == 200:
                    print("❌ FAIL - Query was accepted (unexpected)")
                    results["failed"] += 1
                    results["errors"].append(f"Test {i}: Expected blocking but query was accepted")
                else:
                    print(f"⚠️  UNEXPECTED - Status code: {response.status_code}")
                    results["errors"].append(f"Test {i}: Unexpected status {response.status_code}")
            
        except requests.exceptions.ConnectionError:
            print("❌ ERROR - Could not connect to server (is it running on port 8080?)")
            results["errors"].append(f"Test {i}: Connection error")
            results["failed"] += 1
        except Exception as e:
            print(f"❌ ERROR - {str(e)}")
            results["errors"].append(f"Test {i}: {str(e)}")
            results["failed"] += 1
        
        print()
    
    # Test force override functionality
    print("Testing force override functionality...")
    force_query = "force: What's the weather like today?"
    
    try:
        response = requests.post(f"{base_url}/query", json={
            "model": "gpt-4o-mini",
            "content": test_content,
            "query": force_query,
            "title": test_title
        })
        
        if response.status_code == 200:
            print("✅ PASS - Force override worked")
            results["passed"] += 1
        else:
            print("❌ FAIL - Force override did not work")
            results["failed"] += 1
            results["errors"].append("Force override test failed")
    except Exception as e:
        print(f"❌ ERROR - Force override test failed: {str(e)}")
        results["errors"].append(f"Force override: {str(e)}")
        results["failed"] += 1
    
    print()
    print("=" * 50)
    print("TEST SUMMARY")
    print("=" * 50)
    print(f"✅ Passed: {results['passed']}")
    print(f"❌ Failed: {results['failed']}")
    print(f"📊 Success Rate: {results['passed']/(results['passed'] + results['failed'])*100:.1f}%")
    
    if results["errors"]:
        print(f"\n🔍 Errors:")
        for error in results["errors"]:
            print(f"   - {error}")
    
    if results["failed"] == 0:
        print("\n🎉 All tests passed! Query validation system is working correctly.")
    else:
        print(f"\n⚠️  {results['failed']} test(s) failed. Please review the validation logic.")

def test_performance():
    """Test the performance of validation system"""
    print("\n🚀 Testing Validation Performance...")
    print("=" * 30)
    
    import time
    
    test_content = "This is a test article about artificial intelligence in healthcare."
    test_query = "What is this article about?"
    
    start_time = time.time()
    
    try:
        response = requests.post("http://localhost:8080/query", json={
            "model": "gpt-4o-mini",
            "content": test_content,
            "query": test_query,
            "title": "AI in Healthcare"
        })
        
        end_time = time.time()
        total_time = (end_time - start_time) * 1000  # Convert to milliseconds
        
        print(f"⏱️  Total request time: {total_time:.2f}ms")
        
        if total_time < 2000:  # Less than 2 seconds
            print("✅ Performance: Good (under 2 seconds)")
        elif total_time < 5000:  # Less than 5 seconds
            print("⚠️  Performance: Acceptable (2-5 seconds)")
        else:
            print("❌ Performance: Slow (over 5 seconds)")
            
    except Exception as e:
        print(f"❌ Performance test failed: {str(e)}")

if __name__ == "__main__":
    print("🔍 Query Validation System Test Suite")
    print("=" * 50)
    print("Make sure the Flask app is running on localhost:8080")
    print("Run: python app.py")
    print()
    
    input("Press Enter to start tests...")
    
    test_query_validation()
    test_performance()
    
    print("\n✨ Testing complete!")
