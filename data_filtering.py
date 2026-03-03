def filter_by_keyword(articles, keyword):
    """Filter articles by keyword in title or description."""
    return [article for article in articles 
            if keyword.lower() in article.get('title', '').lower() 
            or keyword.lower() in article.get('description', '').lower()]

def filter_by_source(articles, source):
    """Filter articles by news source."""
    return [article for article in articles 
            if article.get('source', {}).get('name', '') == source]

def sort_by_date(articles, reverse=True):
    """Sort articles by publication date."""
    return sorted(articles, 
                 key=lambda x: x.get('publishedAt', ''), 
                 reverse=reverse)
