import requests
from api_keys import NEWSAPI_KEY
from datetime import datetime, timedelta
import json
import os
from LLM_Article_Analysis import run_llm_analysis_if_needed
from country_extraction import process_and_cache_countries

# Cache file path
CACHE_FILE = 'news_cache.json'

# Accepted news sources for supply chain disruption news
ACCEPTED_SOURCES = [
    'australian-financial-review',
    'bloomberg',
    'business-insider',
    'financial-post',
    'fortune',
    'the-wall-street-journal',
    'al-jazeera-english',
    'associated-press',
    'axios',
    'bbc-news',
    'breitbart-news',
    'cbc-news',
    'cbs-news',
    'cnn',
    'fox-news',
    'google-news',
    'google-news-in',
    'independent',
    'msnbc',
    'nbc-news',
    'national-review',
    'news-com-au',
    'news24',
    'newsweek',
    'politico',
    'rte',
    'reuters',
    'the-globe-and-mail',
    'the-hill',
    'the-hindu',
    'the-times-of-india',
    'the-washington-post',
    'the-washington-times',
    'usa-today',
    'xinhua-net',
    'medical-news-today',
    'national-geographic',
    'new-scientist',
    'ars-technica',
    'crypto-coins-news',
    'engadget',
    'hacker-news',
    'recode',
    'techcrunch',
    'techcrunch-cn',
    'techradar',
    'the-next-web',
    'the-verge',
    'wired'
]

# Supply chain disruption keywords organized by category

# 1. Natural Disasters & Weather Events
NAT_DISASTER_KEYWORDS = [
    'earthquake',
    'flood',
    'hurricane'
]

# 2. Geopolitical & Military Conflicts
GEOPOLITIC_KEYWORDS = [
    'sanctions',
    'trade war',
    'military',
    'invasion'
]

# 3. Transportation & Infrastructure Disruptions
TRANSPORT_DISRUPTIONS_KEYWORDS = [
    'port',
    'canal',
    'airport',
    'rail'
]

# 4. Economic & Financial Crises
ECONOMIC_CRISIS_KEYWORDS = [
    'currency',
    'inflation',
    'banking',
    'recession'
]

# 5. Health & Safety Emergencies
HEALTH_SAFETY_KEYWORDS = [
    'pandemic'
]

# 6. Regulatory & Policy Changes
REGULATORY_KEYWORDS = [
    'export',
    'import',
    'trade',
    'regulatory',
    'customs'
]

# 7. Technology & Cyber Disruptions
TECH_CYBER_KEYWORDS = [
    'cyberattack',
    'data breach',
    'ransomware'
]

# 8. Resource & Material Shortages
RESOURCE_SHORTAGE_KEYWORDS = [
    'chip shortage',
    'material',
    'energy',
    'labor'
]

# 9. Corporate & Industry-Specific Issues
CORPORATE_KEYWORDS = [
    'foxconn',
    'wistron',
    'compall',
    'pcba',
    'dell'
]

# 10. Generic Supply Chain & Logistics
GENERIC_KEYWORDS = [
    'freight',
    'logistics',
    'shipping'
]

# Combined list of all keywords for API queries
ALL_SUPPLY_CHAIN_KEYWORDS = (
    NAT_DISASTER_KEYWORDS + 
    GEOPOLITIC_KEYWORDS + 
    TRANSPORT_DISRUPTIONS_KEYWORDS + 
    ECONOMIC_CRISIS_KEYWORDS + 
    HEALTH_SAFETY_KEYWORDS + 
    REGULATORY_KEYWORDS + 
    TECH_CYBER_KEYWORDS + 
    RESOURCE_SHORTAGE_KEYWORDS + 
    CORPORATE_KEYWORDS +
    GENERIC_KEYWORDS
)

# Category mapping for post-processing
CATEGORY_MAPPING = {
    'Natural Disasters': NAT_DISASTER_KEYWORDS,
    'Geopolitical': GEOPOLITIC_KEYWORDS,
    'Transportation': TRANSPORT_DISRUPTIONS_KEYWORDS,
    'Economic Crisis': ECONOMIC_CRISIS_KEYWORDS,
    'Health & Safety': HEALTH_SAFETY_KEYWORDS,
    'Regulatory': REGULATORY_KEYWORDS,
    'Technology & Cyber': TECH_CYBER_KEYWORDS,
    'Resource Shortage': RESOURCE_SHORTAGE_KEYWORDS,
    'Corporate': CORPORATE_KEYWORDS,
    'General Supply Chain': GENERIC_KEYWORDS
}

def load_cache():
    """Load cache from file."""
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, 'r') as f:
                cache_data = json.load(f)
                # Convert timestamp string back to datetime
                if cache_data.get('timestamp'):
                    cache_data['timestamp'] = datetime.fromisoformat(cache_data['timestamp'])
                return cache_data
        except (json.JSONDecodeError, ValueError):
            # If file is corrupted, start fresh
            pass
    return {'data': None, 'timestamp': None}

def save_cache(data, timestamp):
    """Save cache to file."""
    cache_data = {
        'data': data,
        'timestamp': timestamp.isoformat()  # Convert datetime to string for JSON
    }
    with open(CACHE_FILE, 'w') as f:
        json.dump(cache_data, f)

def merge_and_limit_articles(existing_articles, new_articles, max_articles=1000):
    """Merge new articles into existing cache, deduplicate by URL, and keep only the newest max_articles by publishedAt."""
    # Use a dict keyed by URL for deduplication
    article_dict = {}
    for article in existing_articles + new_articles:
        url = article.get('url')
        if url:
            # Always keep the latest version of the article (newest publishedAt)
            if url not in article_dict:
                article_dict[url] = article
            else:
                # If duplicate, keep the one with the latest publishedAt
                old_date = article_dict[url].get('publishedAt', '')
                new_date = article.get('publishedAt', '')
                if new_date > old_date:
                    article_dict[url] = article
    # Sort all articles by publishedAt descending (newest first)
    sorted_articles = sorted(article_dict.values(), key=lambda a: a.get('publishedAt', ''), reverse=True)
    # Keep only the newest max_articles
    return sorted_articles[:max_articles]

def fetch_news(cache_minutes=1):
    """Fetch news articles from NewsAPI with file-based caching and categorization. Upgraded to keep up to 1000 articles."""
    # Load cache from file
    cache = load_cache()
    existing_articles = cache['data'] if cache['data'] is not None else []
    
    # Check if cache is valid
    if (existing_articles and 
        cache['timestamp'] is not None and 
        datetime.now() - cache['timestamp'] < timedelta(minutes=cache_minutes)):
        return existing_articles
    
    # Build query string from keywords
    query = ' OR '.join(f'"{keyword}"' for keyword in ALL_SUPPLY_CHAIN_KEYWORDS)
    
    # Build sources string from accepted sources (comma-separated)
    sources_string = ','.join(ACCEPTED_SOURCES)
    
    # Fetch fresh data
    url = "https://newsapi.org/v2/everything"  # Use 'everything' endpoint for better keyword search
    params = {
        'apiKey': NEWSAPI_KEY,
        'q': query,  # Dynamic query built from keywords list
        'sources': sources_string,  # Filter by accepted sources only
        'pageSize': 100,  # Increased for better results
        'sortBy': 'publishedAt',  # Sort by most recent
        'from': (datetime.now() - timedelta(days=7)).isoformat()  # Last 7 days only
    }
    
    response = requests.get(url, params=params)
    if response.status_code == 200:
        articles = response.json().get('articles', [])
        # Add categorization to articles
        categorized_articles = categorize_articles(articles)
        # Merge with existing cache, deduplicate, and limit to 1000
        merged_articles = merge_and_limit_articles(existing_articles, categorized_articles, max_articles=1000)
        # Save merged articles to cache
        save_cache(merged_articles, datetime.now())
        
        # Extract and cache countries from new articles
        try:
            process_and_cache_countries(merged_articles)
        except Exception as e:
            print(f"Warning: Country extraction failed: {e}")
        
        # Run LLM analysis on new articles
        try:
            run_llm_analysis_if_needed()
        except Exception as e:
            print(f"Warning: LLM analysis failed: {e}")
        
        return merged_articles
    return existing_articles

def categorize_article(article):
    """Determine which categories an article belongs to based on keywords."""
    title = (article.get('title') or '').lower()
    description = (article.get('description') or '').lower()
    content = (article.get('content') or '').lower()
    
    # Combine all text for keyword matching
    full_text = f"{title} {description} {content}"
    
    categories = []
    for category_name, keywords in CATEGORY_MAPPING.items():
        # Check if any keyword from this category appears in the article
        if any(keyword.lower() in full_text for keyword in keywords):
            categories.append(category_name)
    
    # If no specific categories found, default to General Supply Chain
    if not categories:
        categories.append('General Supply Chain')
    
    return categories

def categorize_articles(articles):
    """Add category information to each article."""
    categorized_articles = []
    
    for article in articles:
        # Create a copy of the article with category information
        categorized_article = article.copy()
        categorized_article['categories'] = categorize_article(article)
        categorized_article['primary_category'] = categorized_article['categories'][0] if categorized_article['categories'] else 'General Supply Chain'
        categorized_articles.append(categorized_article)
    
    return categorized_articles

def get_articles_by_category(articles, category_name):
    """Filter articles by a specific category."""
    return [article for article in articles if category_name in article.get('categories', [])]

def get_category_summary(articles):
    """Get a summary of article counts by category."""
    category_counts = {}
    for article in articles:
        for category in article.get('categories', []):
            category_counts[category] = category_counts.get(category, 0) + 1
    return category_counts

def get_category_overview(articles, category_name):
    """Get detailed overview for a specific category including sources."""
    category_articles = get_articles_by_category(articles, category_name)
    
    # Count total articles
    total_count = len(category_articles)
    
    # Get unique sources for this category
    sources = set()
    for article in category_articles:
        source_name = article.get('source', {}).get('name', '')
        if source_name:
            sources.add(source_name)
    
    return {
        'total_articles': total_count,
        'sources': sorted(list(sources)),
        'source_count': len(sources)
    }
