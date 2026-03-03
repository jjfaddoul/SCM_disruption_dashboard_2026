import json
from collections import Counter, defaultdict
from datetime import datetime

# Path to the news cache file
NEWS_CACHE_PATH = 'news_cache.json'

def overview_news_cache(cache_path):
    with open(cache_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    articles = data.get('data', [])
    print(f"Total number of articles: {len(articles)}\n")

    # Unique sources and count per source
    sources = [a['source']['name'] for a in articles if 'source' in a and 'name' in a['source']]
    source_counts = Counter(sources)
    print(f"Number of unique sources: {len(source_counts)}")
    print("Articles per source:")
    for source, count in source_counts.most_common():
        print(f"  {source}: {count}")
    print()

    # Categories and primary_category
    all_categories = []
    primary_categories = []
    for a in articles:
        all_categories.extend(a.get('categories', []))
        if 'primary_category' in a:
            primary_categories.append(a['primary_category'])
    cat_counts = Counter(all_categories)
    prim_cat_counts = Counter(primary_categories)
    print("Articles per category:")
    for cat, count in cat_counts.most_common():
        print(f"  {cat}: {count}")
    print()
    print("Articles per primary_category:")
    for cat, count in prim_cat_counts.most_common():
        print(f"  {cat}: {count}")
    print()

    # Date range
    dates = [a['publishedAt'] for a in articles if 'publishedAt' in a]
    if dates:
        date_objs = [datetime.fromisoformat(d.replace('Z', '+00:00')) for d in dates]
        print(f"Date range: {min(date_objs)} to {max(date_objs)}\n")

    # Most recent article titles
    sorted_articles = sorted(articles, key=lambda x: x.get('publishedAt', ''), reverse=True)
    print("Most recent 5 articles:")
    for a in sorted_articles[:5]:
        print(f"  - {a.get('title', 'No Title')}")
    print()

    # Duplicate URLs
    urls = [a.get('url') for a in articles if 'url' in a]
    url_counts = Counter(urls)
    duplicates = [url for url, count in url_counts.items() if count > 1]
    if duplicates:
        print("Duplicate article URLs:")
        for url in duplicates:
            print(f"  {url} (count: {url_counts[url]})")
    else:
        print("No duplicate article URLs found.")

if __name__ == "__main__":
    overview_news_cache(NEWS_CACHE_PATH)
