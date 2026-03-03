import json
import os
import time
import hashlib
from datetime import datetime
import google.generativeai as genai
from api_keys import GEMINI_API_KEY

# Cache file paths
NEWS_CACHE_FILE = 'news_cache.json'
LLM_CACHE_FILE = 'llm_analysis_cache.json'

# Configure Gemini
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemma-3-27b-it')  # Updated model name

def load_news_cache():
    """Load the news cache file."""
    if os.path.exists(NEWS_CACHE_FILE):
        try:
            with open(NEWS_CACHE_FILE, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, ValueError):
            return None
    return None

def load_llm_cache():
    """Load the LLM analysis cache file."""
    if os.path.exists(LLM_CACHE_FILE):
        try:
            with open(LLM_CACHE_FILE, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, ValueError):
            pass
    return {}

def save_llm_cache(cache_data):
    """Save the LLM analysis cache to file."""
    with open(LLM_CACHE_FILE, 'w') as f:
        json.dump(cache_data, f, indent=2)

def generate_article_hash(article):
    """Generate a unique hash for an article based on its URL and title."""
    url = article.get('url', '')
    title = article.get('title', '')
    content = f"{url}{title}"
    return hashlib.md5(content.encode()).hexdigest()

def extract_article_text(article):
    """Extract relevant text from an article for LLM analysis."""
    title = article.get('title', '')
    description = article.get('description', '')
    content = article.get('content', '')
    
    # Combine all text, with preference for title and description
    full_text = f"Title: {title}\n"
    if description:
        full_text += f"Description: {description}\n"
    if content:
        # Limit content to avoid token limits
        content_preview = content[:500] + "..." if len(content) > 500 else content
        full_text += f"Content: {content_preview}"
    
    return full_text.strip()

def analyze_article_with_llm(article_text, max_retries=3):
    """Send article text to Gemini for supply chain impact analysis."""
    prompt = f"""Analyze the following news article and provide a one-sentence explanation of how the topic discussed might affect global supply chains. Focus on potential disruptions, delays, cost impacts, or other supply chain implications. Be as brief as possible.

Article:
{article_text}

Response (one sentence only):"""

    for attempt in range(max_retries):
        try:
            response = model.generate_content(prompt)
            
            if response.text:
                # Clean up the response
                analysis = response.text.strip()
                # Ensure it's a single sentence
                if not analysis.endswith('.'):
                    analysis += '.'
                return analysis
            else:
                print(f"Empty response from Gemini on attempt {attempt + 1}")
                
        except Exception as e:
            print(f"Error calling Gemini API on attempt {attempt + 1}: {e}")
            if attempt < max_retries - 1:
                # Wait before retrying (exponential backoff)
                time.sleep(2 ** attempt)
            
    return "Supply chain impact analysis unavailable."

def check_news_cache_updated():
    """Check if the news cache has been updated since last LLM analysis."""
    if not os.path.exists(NEWS_CACHE_FILE):
        return False
    
    # Get modification time of news cache
    news_cache_mtime = os.path.getmtime(NEWS_CACHE_FILE)
    
    # Check if LLM cache exists and get its modification time
    if os.path.exists(LLM_CACHE_FILE):
        llm_cache_mtime = os.path.getmtime(LLM_CACHE_FILE)
        # Return True if news cache is newer than LLM cache
        return news_cache_mtime > llm_cache_mtime
    
    # If LLM cache doesn't exist, we need to process
    return True

def process_articles_for_llm_analysis():
    """Main function to process all articles in news cache for LLM analysis."""
    print("Starting LLM analysis of cached articles...")
    
    # Load caches
    news_cache = load_news_cache()
    if not news_cache or 'data' not in news_cache:
        print("No news cache found or cache is empty.")
        return
    
    articles = news_cache['data']
    llm_cache = load_llm_cache()
    
    print(f"Found {len(articles)} articles to analyze...")
    
    new_analyses = 0
    cached_analyses = 0
    
    for i, article in enumerate(articles):
        # Generate unique hash for this article
        article_hash = generate_article_hash(article)
        
        # Check if we already have analysis for this article
        if article_hash in llm_cache:
            cached_analyses += 1
            print(f"Article {i+1}/{len(articles)}: Using cached analysis")
            continue
        
        # Extract article text
        article_text = extract_article_text(article)
        
        if not article_text:
            print(f"Article {i+1}/{len(articles)}: No text content, skipping")
            continue
        
        print(f"Article {i+1}/{len(articles)}: Analyzing with Gemini...")
        
        # Get LLM analysis
        analysis = analyze_article_with_llm(article_text)
        
        # Cache the result
        llm_cache[article_hash] = {
            'analysis': analysis,
            'timestamp': datetime.now().isoformat(),
            'article_url': article.get('url', ''),
            'article_title': article.get('title', '')
        }
        
        new_analyses += 1
        
        # Save cache after each analysis to avoid losing progress
        save_llm_cache(llm_cache)
        
        # Rate limiting - be respectful to the API
        time.sleep(1)  # 1 second delay between requests
        
        print(f"Analysis complete: {analysis[:100]}...")
    
    print(f"\nLLM Analysis Summary:")
    print(f"- New analyses: {new_analyses}")
    print(f"- Cached analyses: {cached_analyses}")
    print(f"- Total articles: {len(articles)}")
    
    return llm_cache

def get_article_analysis(article):
    """Get LLM analysis for a specific article."""
    llm_cache = load_llm_cache()
    article_hash = generate_article_hash(article)
    
    if article_hash in llm_cache:
        return llm_cache[article_hash]['analysis']
    
    return None

def run_llm_analysis_if_needed():
    """Run LLM analysis only if news cache has been updated."""
    if check_news_cache_updated():
        print("News cache has been updated. Running LLM analysis...")
        return process_articles_for_llm_analysis()
    else:
        print("News cache hasn't changed since last LLM analysis.")
        return load_llm_cache()

if __name__ == "__main__":
    # Run analysis when script is executed directly
    run_llm_analysis_if_needed()
