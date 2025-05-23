"""
Firecrawl API Diagnostic Script
This script tests the Firecrawl API directly to identify specific issues
and optimal parameters for different types of websites.
"""

import os
import json
import time
from dotenv import load_dotenv
from firecrawl import FirecrawlApp

# Load environment variables
load_dotenv()

class FirecrawlDiagnostics:
    def __init__(self):
        self.api_key = os.getenv("FIRECRAWL_API_KEY")
        if not self.api_key:
            raise ValueError("FIRECRAWL_API_KEY not found in environment variables")
        
        self.firecrawl = FirecrawlApp(api_key=self.api_key)
        self.test_results = []
    
    def test_api_connectivity(self):
        """Test basic API connectivity and authentication"""
        print("🔍 Testing Firecrawl API connectivity...")
        try:
            # Test with a simple, reliable URL
            test_url = "https://example.com"
            result = self.firecrawl.scrape_url(test_url, params={
                'onlyMainContent': True,
                'formats': ['markdown']
            })
            
            if result and 'markdown' in result:
                print("✅ API connectivity successful")
                print(f"   Sample content length: {len(result['markdown'])} characters")
                return True
            else:
                print("❌ API connectivity failed - no content returned")
                return False
                
        except Exception as e:
            print(f"❌ API connectivity failed: {str(e)}")
            return False
    
    def test_url_with_different_params(self, url, test_name=""):
        """Test a URL with different parameter combinations"""
        print(f"\n🧪 Testing URL: {url}")
        if test_name:
            print(f"   Test: {test_name}")
        
        # Different parameter combinations to test
        test_configs = [
            {
                "name": "Basic Markdown",
                "params": {
                    'onlyMainContent': True,
                    'formats': ['markdown']
                }
            },
            {
                "name": "Markdown + HTML Fallback",
                "params": {
                    'onlyMainContent': True,
                    'formats': ['markdown', 'html']
                }
            },
            {
                "name": "With Wait Time",
                "params": {
                    'onlyMainContent': True,
                    'waitFor': 3000,
                    'formats': ['markdown']
                }
            },
            {
                "name": "Full Content (no filter)",
                "params": {
                    'onlyMainContent': False,
                    'formats': ['markdown']
                }
            }
        ]
        
        results = []
        
        for config in test_configs:
            print(f"   📋 Testing: {config['name']}")
            try:
                start_time = time.time()
                result = self.firecrawl.scrape_url(url, params=config['params'])
                duration = time.time() - start_time
                
                if result:
                    content_length = len(result.get('markdown', '')) if result.get('markdown') else 0
                    has_title = bool(result.get('metadata', {}).get('title'))
                    
                    status = "✅ Success"
                    print(f"      {status} - Content: {content_length} chars, Duration: {duration:.2f}s, Title: {has_title}")
                    
                    results.append({
                        "config": config['name'],
                        "success": True,
                        "content_length": content_length,
                        "duration": duration,
                        "has_title": has_title,
                        "error": None
                    })
                else:
                    status = "❌ Failed - No content returned"
                    print(f"      {status}")
                    results.append({
                        "config": config['name'],
                        "success": False,
                        "error": "No content returned"
                    })
                    
            except Exception as e:
                status = f"❌ Failed - {str(e)}"
                print(f"      {status}")
                results.append({
                    "config": config['name'],
                    "success": False,
                    "error": str(e)
                })
                
        self.test_results.append({
            "url": url,
            "test_name": test_name,
            "results": results
        })
        
        return results
    
    def run_comprehensive_tests(self):
        """Run tests on various types of websites"""
        print("🚀 Starting comprehensive Firecrawl diagnostics...\n")
        
        # Test basic connectivity first
        if not self.test_api_connectivity():
            print("❌ Basic API connectivity failed. Check your API key and internet connection.")
            return
        
        # Test URLs of different types
        test_urls = [
            ("https://www.bbc.com/news", "BBC News Article"),
            ("https://techcrunch.com", "TechCrunch Homepage"),
            ("https://medium.com/@example", "Medium Article (if accessible)"),
            ("https://www.wikipedia.org/wiki/Artificial_intelligence", "Wikipedia Article"),
            ("https://github.com/microsoft/vscode", "GitHub Repository"),
            ("https://stackoverflow.com/questions/11227809/why-is-processing-a-sorted-array-faster-than-processing-an-unsorted-array", "StackOverflow Question"),
        ]
        
        for url, description in test_urls:
            try:
                self.test_url_with_different_params(url, description)
                time.sleep(1)  # Rate limiting courtesy
            except KeyboardInterrupt:
                print("\n⏹️ Tests interrupted by user")
                break
            except Exception as e:
                print(f"❌ Unexpected error testing {url}: {str(e)}")
    
    def generate_report(self):
        """Generate a summary report of all tests"""
        print("\n" + "="*60)
        print("📊 FIRECRAWL DIAGNOSTIC REPORT")
        print("="*60)
        
        total_tests = sum(len(test['results']) for test in self.test_results)
        successful_tests = sum(1 for test in self.test_results for result in test['results'] if result['success'])
        
        print(f"Total tests run: {total_tests}")
        print(f"Successful tests: {successful_tests}")
        print(f"Success rate: {(successful_tests/total_tests*100):.1f}%" if total_tests > 0 else "No tests completed")
        
        # Identify best performing configurations
        config_performance = {}
        for test in self.test_results:
            for result in test['results']:
                config_name = result['config']
                if config_name not in config_performance:
                    config_performance[config_name] = {'success': 0, 'total': 0}
                
                config_performance[config_name]['total'] += 1
                if result['success']:
                    config_performance[config_name]['success'] += 1
        
        print("\n🏆 Configuration Performance:")
        for config, stats in sorted(config_performance.items(), 
                                  key=lambda x: x[1]['success']/x[1]['total'] if x[1]['total'] > 0 else 0, 
                                  reverse=True):
            success_rate = stats['success']/stats['total']*100 if stats['total'] > 0 else 0
            print(f"   {config}: {stats['success']}/{stats['total']} ({success_rate:.1f}%)")
        
        # Common errors
        errors = {}
        for test in self.test_results:
            for result in test['results']:
                if not result['success'] and result.get('error'):
                    error = result['error']
                    errors[error] = errors.get(error, 0) + 1
        
        if errors:
            print("\n⚠️ Common Errors:")
            for error, count in sorted(errors.items(), key=lambda x: x[1], reverse=True):
                print(f"   {error}: {count} occurrences")
        
        print("\n💡 Recommendations:")
        
        # Find best config
        if config_performance:
            best_config = max(config_performance.items(), 
                            key=lambda x: x[1]['success']/x[1]['total'] if x[1]['total'] > 0 else 0)
            print(f"   - Use '{best_config[0]}' configuration for best results")
        
        if successful_tests < total_tests * 0.8:  # Less than 80% success rate
            print("   - Consider implementing retry logic with exponential backoff")
            print("   - Add fallback mechanisms for failed requests")
        
        if any("timeout" in str(result.get('error', '')).lower() for test in self.test_results for result in test['results']):
            print("   - Increase timeout values for better success rates")
        
        print("   - Implement domain-specific parameter optimization")
        print("   - Add content quality validation after scraping")
        
        # Save detailed results to file
        with open('firecrawl_diagnostic_results.json', 'w') as f:
            json.dump(self.test_results, f, indent=2)
        print(f"\n📄 Detailed results saved to: firecrawl_diagnostic_results.json")

def main():
    """Run the diagnostic tests"""
    try:
        diagnostics = FirecrawlDiagnostics()
        diagnostics.run_comprehensive_tests()
        diagnostics.generate_report()
    except Exception as e:
        print(f"❌ Diagnostic script failed: {str(e)}")
        print("Please check your .env file and ensure FIRECRAWL_API_KEY is set correctly.")

if __name__ == "__main__":
    main()
