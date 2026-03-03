"""
Detailed API Diagnostic Test
Tests API connectivity and query parameters
"""

import requests
from api_keys import NEWSAPI_KEY
from datetime import datetime, timedelta
from data_fetcher import ALL_SUPPLY_CHAIN_KEYWORDS

def quick_test():
    # this function performs a quick test to ensure compliance with the API query length limits
    print("🔍 QUICK KEYWORD TEST")
    query = ' OR '.join(f'"{k}"' for k in ALL_SUPPLY_CHAIN_KEYWORDS)
    print(f"Keywords: {len(ALL_SUPPLY_CHAIN_KEYWORDS)}")
    print(f"Query length: {len(query)}")
    print(f"Status: {'✅ OK' if len(query) <= 500 else '❌ TOO LONG'}")
    print(f"Keywords: {ALL_SUPPLY_CHAIN_KEYWORDS}")


def test_api_connectivity():
    """Test basic API connectivity and parameters."""
    print("🔍 DETAILED API DIAGNOSTIC")
    print("=" * 50)
    
    # Test 1: Check API key
    print("1️⃣ Testing API Key...")
    if NEWSAPI_KEY and len(NEWSAPI_KEY) > 10:
        print(f"   ✅ API key exists (length: {len(NEWSAPI_KEY)})")
        print(f"   🔑 Key preview: {NEWSAPI_KEY[:8]}...{NEWSAPI_KEY[-4:]}")
    else:
        print("   ❌ API key missing or invalid")
        return
    
    # Test 2: Simple API call
    print("\n2️⃣ Testing basic API connectivity...")
    try:
        url = "https://newsapi.org/v2/everything"
        params = {
            'apiKey': NEWSAPI_KEY,
            'q': 'supply chain',  # Simple query
            'language': 'en',
            'pageSize': 5,  # Small request
            'sortBy': 'publishedAt'
        }
        
        print(f"   🌐 Making request to: {url}")
        print(f"   📝 Query: {params['q']}")
        
        response = requests.get(url, params=params)
        print(f"   📊 Response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            total_results = data.get('totalResults', 0)
            articles_count = len(data.get('articles', []))
            print(f"   ✅ API call successful!")
            print(f"   📈 Total results available: {total_results}")
            print(f"   📋 Articles returned: {articles_count}")
            
            if articles_count > 0:
                sample = data['articles'][0]
                print(f"   📰 Sample title: {sample.get('title', 'N/A')[:50]}...")
            
        elif response.status_code == 401:
            print("   ❌ Authentication failed - Invalid API key")
        elif response.status_code == 429:
            print("   ❌ Rate limit exceeded - Too many requests")
        else:
            print(f"   ❌ API error: {response.status_code}")
            try:
                error_data = response.json()
                print(f"   💬 Error message: {error_data.get('message', 'Unknown error')}")
            except:
                print(f"   💬 Response text: {response.text[:100]}...")
                
    except Exception as e:
        print(f"   ❌ Connection error: {str(e)}")
        return
    
    # Test 3: Test our complex query
    if response.status_code == 200:
        print("\n3️⃣ Testing complex keyword query...")
        
        # Import fresh keywords from data_fetcher
        import importlib
        import data_fetcher
        importlib.reload(data_fetcher)  # Reload to get latest changes
        
        # Build our actual query
        query = ' OR '.join(f'"{keyword}"' for keyword in data_fetcher.ALL_SUPPLY_CHAIN_KEYWORDS)
        print(f"   📝 Keyword count: {len(data_fetcher.ALL_SUPPLY_CHAIN_KEYWORDS)}")
        print(f"   📏 Query length: {len(query)} characters")
        print(f"   🔍 Query preview: {query[:100]}...")
        
        # Test if query is too long
        if len(query) > 500:  # NewsAPI has query length limits
            print("   ⚠️  Warning: Query might be too long for NewsAPI")
        else:
            print("   ✅ Query length is within NewsAPI limits!")
            
        params['q'] = query
        params['pageSize'] = 10
        params['from'] = (datetime.now() - timedelta(days=7)).isoformat()
        
        try:
            response = requests.get(url, params=params)
            print(f"   📊 Complex query status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                total_results = data.get('totalResults', 0)
                articles_count = len(data.get('articles', []))
                print(f"   ✅ Complex query successful!")
                print(f"   📈 Total results: {total_results}")
                print(f"   📋 Articles returned: {articles_count}")
                
                if articles_count == 0:
                    print("   💡 Suggestion: Keywords might be too specific")
                    print("   💡 Try broader terms or different time range")
                    
            else:
                print(f"   ❌ Complex query failed: {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   💬 Error: {error_data.get('message', 'Unknown')}")
                except:
                    pass
                    
        except Exception as e:
            print(f"   ❌ Complex query error: {str(e)}")
    
    # Test 4: Alternative simple queries
    print("\n4️⃣ Testing alternative queries...")
    test_queries = [
        "logistics",
        "supply chain disruption", 
        "shipping",
        "manufacturing"
    ]
    
    for query in test_queries:
        try:
            params = {
                'apiKey': NEWSAPI_KEY,
                'q': query,
                'language': 'en',
                'pageSize': 5,
                'sortBy': 'publishedAt'
            }
            
            response = requests.get(url, params=params)
            if response.status_code == 200:
                data = response.json()
                count = len(data.get('articles', []))
                print(f"   ✅ '{query}': {count} articles")
            else:
                print(f"   ❌ '{query}': Failed ({response.status_code})")
                
        except Exception as e:
            print(f"   ❌ '{query}': Error ({str(e)})")
    
    print("\n" + "=" * 50)
    print("🏁 DIAGNOSTIC COMPLETED")
    print("=" * 50)

if __name__ == "__main__":
    test_api_connectivity()
