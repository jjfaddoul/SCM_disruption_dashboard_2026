"""
Impact Assessment Module for Supply Chain Disruption Dashboard

This module provides functionality to assess the impact level of news articles
based on scale and scope keywords found in article titles and descriptions,
enhanced with Named Entity Recognition (NER) for more accurate impact assessment.
"""

import re
from collections import Counter

# Try to import spaCy for NER, fall back to keyword-only if not available
try:
    import spacy
    nlp = spacy.load("en_core_web_sm")
    NER_AVAILABLE = True
except (ImportError, OSError):
    print("Warning: spaCy not available. Install with: pip install spacy && python -m spacy download en_core_web_sm")
    nlp = None
    NER_AVAILABLE = False


### Key Words used to assess impact


## List of general Impact keywords to assess Scale & Scope
# Scale & Scope Keywords for Impact Assessment
HIGH_IMPACT_KEYWORDS = [
    'global', 'worldwide', 'international', 'massive', 'major', 'critical', 
    'severe', 'widespread', 'catastrophic', 'crisis', 'shutdown', 'halt',
    'billions', 'shortage', 'disruption', 'collapse', 'emergency',
    'devastating', 'unprecedented', 'industry-wide'
]

MEDIUM_IMPACT_KEYWORDS = [
    'regional', 'significant', 'substantial', 'moderate', 'delay', 'slowdown',
    'reduced', 'limited', 'affected', 'impacted', 'hundreds', 'thousands',
    'notable', 'considerable', 'important', 'serious', 'partial', 'some',
    'multiple', 'several', 'various', 'numerous'
]

LOW_IMPACT_KEYWORDS = [
    'local', 'minor', 'small', 'temporary', 'brief', 'isolated', 'limited',
    'recovering', 'stabilizing', 'minimal', 'slight', 'single', 'one',
    'individual', 'specific', 'localized', 'contained', 'manageable',
    'improving', 'restored', 'resolved'
]

## List of Named Entity Recognition (NER) keywords for critical entities
# Critical Supply Chain Entities for NER Analysis
CRITICAL_PORTS = {
    'port of los angeles', 'port of long beach', 'port of shanghai', 
    'port of singapore', 'port of rotterdam', 'port of hamburg',
    'suez canal', 'panama canal', 'strait of hormuz', 'strait of malacca',
    'port of shenzhen', 'port of ningbo', 'port of busan', 'port of hong kong'
}

CRITICAL_COMPANIES = {
    'apple', 'amazon', 'walmart', 'toyota', 'samsung', 'tsmc', 
    'foxconn', 'maersk', 'fedex', 'ups', 'dhl', 'cosco', 'msc',
    'intel', 'nvidia', 'qualcomm', 'microsoft', 'google', 'tesla',
    'boeing', 'airbus', 'caterpillar', 'general motors', 'ford',
    'volkswagen', 'byd', 'alibaba', 'tencent', 'asml', 'dell', 'hp'
}

CRITICAL_COUNTRIES = {
    'china', 'united states', 'germany', 'japan', 'south korea', 
    'taiwan', 'singapore', 'netherlands', 'india', 'vietnam',
    'mexico', 'canada', 'united kingdom', 'france', 'italy',
    'thailand', 'malaysia', 'indonesia', 'philippines', 'turkey'
}

CRITICAL_INDUSTRIES = {
    'semiconductor', 'automotive', 'electronics', 'energy', 
    'pharmaceutical', 'aerospace', 'shipping', 'logistics',
    'manufacturing', 'steel', 'aluminum', 'lithium', 'rare earth',
    'oil', 'gas', 'coal', 'copper', 'nickel', 'cobalt'
}

# Industry sector mappings for detection
INDUSTRY_KEYWORDS = {
    'automotive': ['toyota', 'ford', 'gm', 'volkswagen', 'automotive', 'car', 'vehicle', 'auto'],
    'technology': ['pcba', 'dell', 'apple', 'microsoft', 'google', 'semiconductor', 'chip', 'tech', 'software'],
    'energy': ['oil', 'gas', 'renewable', 'power', 'energy', 'electricity', 'fuel', 'coal'],
    'shipping': ['maersk', 'shipping', 'port', 'cargo', 'container', 'vessel', 'freight'],
    'aerospace': ['boeing', 'airbus', 'aircraft', 'aviation', 'airline', 'flight'],
    'pharmaceuticals': ['pharmaceutical', 'medicine', 'drug', 'vaccine', 'healthcare', 'medical'],
    'electronics': ['electronics', 'smartphone', 'computer', 'display', 'battery'],
    'manufacturing': ['manufacturing', 'factory', 'production', 'assembly', 'industrial']
}

# NER Functions

# Step 4: calculate scroing for keyword, NER and geographic scope
def calculate_entity_score(article):
    """
    Calculate a normalized entity-based score (0-10) based on critical entities.

    Args:
        article (dict): Article dictionary containing title, description, etc.

    Returns:
        float: Entity score (0-10)
    """
    if not NER_AVAILABLE:
        return 1.0  # Fallback to minimum score if NER is not available

    title = (article.get('title') or '').lower()
    description = (article.get('description') or '').lower()
    content = (article.get('content') or '').lower()
    full_text = f"{title} {description} {content}"

    doc = nlp(full_text)
    detected_entities = set()

    for ent in doc.ents:
        if ent.label_ in ['ORG', 'GPE', 'FAC', 'LOC']:
            detected_entities.add(ent.text.lower())

    for critical_entity in CRITICAL_PORTS | CRITICAL_COMPANIES | CRITICAL_COUNTRIES:
        if critical_entity in full_text:
            detected_entities.add(critical_entity)

    score = 0
    score += sum(4 for entity in CRITICAL_PORTS if entity in detected_entities)
    score += sum(3 for entity in CRITICAL_COMPANIES if entity in detected_entities)
    score += sum(2 for entity in CRITICAL_COUNTRIES if entity in detected_entities)

    entity_count = len(detected_entities)
    if entity_count >= 5:
        score += 2
    elif entity_count >= 3:
        score += 1

    return max(1.0, min(10.0, score))

def calculate_keyword_score(article):
    """
    Calculate a normalized keyword-based score (0-10).
    
    Args:
        article (dict): Article dictionary containing title, description, etc.
        
    Returns:
        float: Keyword score (0-10)
    """
    # Extract text content with safe handling of None values
    title = (article.get('title') or '').lower()
    description = (article.get('description') or '').lower()
    content = (article.get('content') or '').lower()
    
    # Combine all text for analysis (title weighted more heavily)
    full_text = f"{title} {title} {description} {content}"  # Title appears twice for emphasis
    
    # Count keyword matches
    high_score = sum(1 for keyword in HIGH_IMPACT_KEYWORDS if keyword in full_text)
    medium_score = sum(1 for keyword in MEDIUM_IMPACT_KEYWORDS if keyword in full_text)
    low_score = sum(1 for keyword in LOW_IMPACT_KEYWORDS if keyword in full_text)
    
    # Calculate weighted score (0-10 scale)
    # High impact keywords are worth more, low impact keywords reduce score
    keyword_score = (high_score * 3) + (medium_score * 1.5) - (low_score * 0.5)
    
    # Normalize to 0-10 scale and ensure minimum of 1
    normalized_score = max(1, min(10, keyword_score))
    
    return normalized_score

def calculate_geographic_scope_score(article):
    """
    Calculate score based on geographic scope (0-10).
    Automatically determines geographic scope from article content.
    
    Args:
        article: Article dictionary containing title, description, content
        
    Returns:
        float: Geographic scope score (0-10)
    """
    # Extract text for analysis
    title = (article.get('title') or '').lower()
    description = (article.get('description') or '').lower()
    content = (article.get('content') or '').lower()
    full_text = f"{title} {description} {content}"
    
    # Keywords indicating global scope
    global_keywords = ['global', 'worldwide', 'international', 'multiple countries', 'cross-border', 'multinational']
    # Keywords indicating regional scope
    regional_keywords = ['region', 'regional', 'continent', 'area', 'zone']
    # Keywords indicating local scope
    local_keywords = ['local', 'city', 'town', 'facility', 'plant', 'warehouse']
    
    # Count occurrences
    global_count = sum(1 for keyword in global_keywords if keyword in full_text)
    regional_count = sum(1 for keyword in regional_keywords if keyword in full_text)
    local_count = sum(1 for keyword in local_keywords if keyword in full_text)
    
    # Determine scope based on highest count
    if global_count > 0:
        geographic_scope = "Global"
    elif regional_count > 0:
        geographic_scope = "Regional"
    elif local_count > 0:
        geographic_scope = "Local"
    else:
        # Default to International if no specific scope indicators
        geographic_scope = "International"
    
    scope_scores = {
        "Global": 10,
        "International": 7,
        "Regional": 4,
        "Local": 1
    }
    
    return scope_scores.get(geographic_scope, 1)

# Step 3: the Enhanced weighted scoring system
def assess_impact_weighted(article):
    """
    Weighted scoring system for impact assessment.
    Balances keywords, entities, and criticality with proper weighting.
    
    Args:
        article (dict): Article dictionary containing title, description, etc.
        
    Returns:
        dict: Weighted impact assessment with detailed breakdown
    """
    # Calculate individual component scores (0-10 scale)
    keyword_score = calculate_keyword_score(article)
    entity_score = calculate_entity_score(article)
    geo_scope_score = calculate_geographic_scope_score(article)
    
    # Default moderate criticality
    criticality_score = 5  
    
    # Weighted final score calculation
    if NER_AVAILABLE:
        # Full weighted scoring with NER
        final_score = (
            keyword_score * 0 +         # 0% weight to key_wrods if entity is available
            entity_score * 0.8 +        # 80% weight to entities (most important)
            criticality_score * 0.10 +  # 10% weight to criticality
            geo_scope_score * 0.10      # 10% weight to geographic scope
        )
    else:
        # Fallback to keyword-only with higher weight
        final_score = keyword_score
    
    # Determine impact level based on weighted score
    if final_score >= 7.0:
        impact_level = "High"
    elif final_score >= 4.0:
        impact_level = "Medium"
    else:
        impact_level = "Low"
    
    
    return {
        'overall_score': round(final_score, 2),
        'keyword_score': round(keyword_score, 2),
        'entity_score': round(entity_score, 2),
        'criticality_score': round(criticality_score, 2),
        'geographic_score': round(geo_scope_score, 2),
        'impact_level': impact_level,
        'weights': {
            'keywords': 0 if NER_AVAILABLE else 1.0,
            'entities': 0.8 if NER_AVAILABLE else 0,
            'criticality': 0.1 if NER_AVAILABLE else 0,
            'geographic_scope': 0.1 if NER_AVAILABLE else 0
        },
        'method': 'weighted_scoring',
        'ner_available': NER_AVAILABLE
    }

# Step 2: Main function to assess impact using the best available method
def assess_impact(article):
    """
    Assess the impact level of a news article using enhanced NER-based analysis.
    Automatically uses the best available method (weighted scoring with NER), and falls back to a keyword-only score if NER or the weighted method fails.
    
    Args:
        article (dict): Article dictionary containing title, description, etc.
        
    Returns:
        str: Impact level - 'High', 'Medium', or 'Low'
    """
    if NER_AVAILABLE:
        # Use enhanced weighted scoring system with NER
        try:
            weighted_result = assess_impact_weighted(article)
            return weighted_result['impact_level']
        except Exception:
              # Use calculate_keyword_score to get a normalized score
            score = calculate_keyword_score(article)
            if score >= 7:
                return "High"
            elif score >= 4:
                return "Medium"
            else:
                return "Low"
            
    else:
        # use basic keyword assessment as fallback
        score = calculate_keyword_score(article)
        if score >= 7:
            return "High"
        elif score >= 4:
            return "Medium"
        else:
            return "Low"

# Step 2.1: Secondary function to add badge        
def get_impact_badge(impact_level):
    """
    Get the visual badge (icon + text) for an impact level.
    
    Args:
        impact_level (str): Impact level - 'High', 'Medium', or 'Low'
        
    Returns:
        str: Formatted badge string with icon and text
    """
    badges = {
        "High": "🔴 High Impact",
        "Medium": "🟡 Medium Impact", 
        "Low": "🟢 Low Impact"
    }
    
    return badges.get(impact_level, "⚪ Unknown Impact")


# Step 1: main function called for assessing article impact
def assess_and_format_title(article):
    """
    Assess impact and format the article title with impact badge.
    
    Args:
        article (dict): Article dictionary
        
    Returns:
        str: Formatted title with impact badge
    """
    impact_level = assess_impact(article)
    impact_badge = get_impact_badge(impact_level)
    title = article.get('title', 'No Title')
    
    return f"{impact_badge} | {title}"

