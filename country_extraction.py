import json
from typing import List, Dict, Set
import os

# Try to load the spaCy model, with fallback instructions
nlp = None

# Country name standardization mapping
COUNTRY_STANDARDIZATION = {
    # Common variations to standard names
    'US': 'United States',
    'USA': 'United States',
    'U.S.': 'United States',
    'America': 'United States',
    'UK': 'United Kingdom',
    'Britain': 'United Kingdom',
    'EU': 'European Union',
    'UAE': 'United Arab Emirates',
    'Russia': 'Russia',
    'Russian Federation': 'Russia',
    'China': 'China',
    'PRC': 'China',
    "People's Republic of China": 'China',
    'India': 'India',
    'Japan': 'Japan',
    'Germany': 'Germany',
    'France': 'France',
    'Canada': 'Canada',
    'Australia': 'Australia',
    'Brazil': 'Brazil',
    'Mexico': 'Mexico',
    'Italy': 'Italy',
    'Spain': 'Spain',
    'South Korea': 'South Korea',
    'Taiwan': 'Taiwan',
    'Singapore': 'Singapore',
    'Netherlands': 'Netherlands',
    'Switzerland': 'Switzerland',
    'Norway': 'Norway',
    'Sweden': 'Sweden',
    'Denmark': 'Denmark',
    'Finland': 'Finland',
    'Poland': 'Poland',
    'Turkey': 'Turkey',
    'Israel': 'Israel',
    'Saudi Arabia': 'Saudi Arabia',
    'Thailand': 'Thailand',
    'Vietnam': 'Vietnam',
    'Indonesia': 'Indonesia',
    'Malaysia': 'Malaysia',
    'Philippines': 'Philippines',
    'Ukraine': 'Ukraine',
    'Belarus': 'Belarus',
    'Kazakhstan': 'Kazakhstan',
    'Iran': 'Iran',
    'Iraq': 'Iraq',
    'Egypt': 'Egypt',
    'Nigeria': 'Nigeria',
    'South Africa': 'South Africa',
    'Argentina': 'Argentina',
    'Chile': 'Chile',
    'Colombia': 'Colombia',
    'Venezuela': 'Venezuela',
    'New Zealand': 'New Zealand',
    'Pakistan': 'Pakistan',
    'Bangladesh': 'Bangladesh',
    'Sri Lanka': 'Sri Lanka'
}

# Comprehensive list of valid countries (including dependencies, territories, and economic unions)
VALID_COUNTRIES = {
    # Major Countries
    'United States', 'China', 'Russia', 'Germany', 'United Kingdom', 'France', 'Japan', 'India',
    'Italy', 'Brazil', 'Canada', 'South Korea', 'Spain', 'Australia', 'Mexico', 'Indonesia',
    'Netherlands', 'Saudi Arabia', 'Turkey', 'Taiwan', 'Belgium', 'Argentina', 'Ireland',
    'Israel', 'Thailand', 'Nigeria', 'Egypt', 'South Africa', 'Philippines', 'Bangladesh',
    'Vietnam', 'Chile', 'Finland', 'Romania', 'Czech Republic', 'New Zealand', 'Peru',
    'Greece', 'Portugal', 'Iraq', 'Algeria', 'Kazakhstan', 'Qatar', 'Ukraine', 'Morocco',
    'Kuwait', 'Angola', 'Ecuador', 'Ethiopia', 'Kenya', 'Ghana', 'Dominican Republic',
    
    # European Countries
    'Austria', 'Switzerland', 'Belgium', 'Bulgaria', 'Croatia', 'Cyprus', 'Denmark',
    'Estonia', 'Finland', 'Hungary', 'Latvia', 'Lithuania', 'Luxembourg', 'Malta',
    'Poland', 'Slovakia', 'Slovenia', 'Sweden', 'Norway', 'Iceland', 'Liechtenstein',
    'Monaco', 'San Marino', 'Vatican City', 'Andorra', 'Belarus', 'Moldova', 'Serbia',
    'Montenegro', 'Bosnia and Herzegovina', 'North Macedonia', 'Albania', 'Kosovo',
    
    # Asian Countries
    'Afghanistan', 'Armenia', 'Azerbaijan', 'Bahrain', 'Bhutan', 'Brunei', 'Cambodia',
    'Georgia', 'Iran', 'Jordan', 'Kyrgyzstan', 'Laos', 'Lebanon', 'Malaysia', 'Maldives',
    'Mongolia', 'Myanmar', 'Nepal', 'North Korea', 'Oman', 'Pakistan', 'Singapore',
    'Sri Lanka', 'Syria', 'Tajikistan', 'Timor-Leste', 'Turkmenistan', 'United Arab Emirates',
    'Uzbekistan', 'Yemen',
    
    # African Countries
    'Benin', 'Botswana', 'Burkina Faso', 'Burundi', 'Cameroon', 'Cape Verde',
    'Central African Republic', 'Chad', 'Comoros', 'Democratic Republic of the Congo',
    'Republic of the Congo', 'Djibouti', 'Equatorial Guinea', 'Eritrea', 'Eswatini',
    'Gabon', 'Gambia', 'Guinea', 'Guinea-Bissau', 'Ivory Coast', 'Lesotho', 'Liberia',
    'Libya', 'Madagascar', 'Malawi', 'Mali', 'Mauritania', 'Mauritius', 'Mozambique',
    'Namibia', 'Niger', 'Rwanda', 'Sao Tome and Principe', 'Senegal', 'Seychelles',
    'Sierra Leone', 'Somalia', 'South Sudan', 'Sudan', 'Tanzania', 'Togo', 'Tunisia',
    'Uganda', 'Zambia', 'Zimbabwe',
    
    # Americas
    'Antigua and Barbuda', 'Bahamas', 'Barbados', 'Belize', 'Bolivia', 'Colombia',
    'Costa Rica', 'Cuba', 'Dominica', 'El Salvador', 'Grenada', 'Guatemala', 'Guyana',
    'Haiti', 'Honduras', 'Jamaica', 'Nicaragua', 'Panama', 'Paraguay', 'Saint Kitts and Nevis',
    'Saint Lucia', 'Saint Vincent and the Grenadines', 'Suriname', 'Trinidad and Tobago',
    'Uruguay', 'Venezuela',
    
    # Oceania
    'Fiji', 'Kiribati', 'Marshall Islands', 'Micronesia', 'Nauru', 'Palau',
    'Papua New Guinea', 'Samoa', 'Solomon Islands', 'Tonga', 'Tuvalu', 'Vanuatu',
    
    # Economic/Political Unions and Special Entities
    'European Union', 'European Economic Area', 'Eurozone',
    
    # Dependencies and Territories (often mentioned in trade/supply chain news)
    'Hong Kong', 'Macau', 'Puerto Rico', 'Guam', 'American Samoa', 'US Virgin Islands',
    'British Virgin Islands', 'Cayman Islands', 'Bermuda', 'Gibraltar', 'Falkland Islands',
    'French Guiana', 'Martinique', 'Guadeloupe', 'Reunion', 'Mayotte', 'New Caledonia',
    'French Polynesia', 'Greenland', 'Faroe Islands', 'Isle of Man', 'Jersey', 'Guernsey',
    'Norfolk Island', 'Christmas Island', 'Cocos Islands', 'Northern Mariana Islands',
    'Cook Islands', 'Niue', 'Tokelau', 'Aruba', 'Curacao', 'Sint Maarten'
}

# Regions/entities that are NOT countries (to filter out)
NON_COUNTRIES = {
    'Asia', 'Europe', 'Africa', 'North America', 'South America', 'Oceania',
    'Middle East', 'Far East', 'Central Asia', 'Southeast Asia', 'Eastern Europe',
    'Western Europe', 'Northern Europe', 'Southern Europe', 'Central America',
    'Caribbean', 'Scandinavia', 'Baltic States', 'Balkans', 'Mediterranean',
    'Pacific', 'Atlantic', 'Indian Ocean', 'Arctic', 'Antarctic',
    'NATO', 'ASEAN', 'OPEC', 'G7', 'G20', 'BRICS', 'UN', 'WTO',
    'World', 'Global', 'International', 'Worldwide', 'Overseas'
}

# City-to-Country mapping for fallback when no countries are found
CITY_TO_COUNTRY = {
    # Major global cities and supply chain hubs
    'Shanghai': 'China',
    'Beijing': 'China',
    'Shenzhen': 'China',
    'Guangzhou': 'China',
    'Tianjin': 'China',
    'Chongqing': 'China',
    'Wuhan': 'China',
    'Suzhou': 'China',
    'Ningbo': 'China',
    'Qingdao': 'China',
    
    'Tokyo': 'Japan',
    'Osaka': 'Japan',
    'Yokohama': 'Japan',
    'Nagoya': 'Japan',
    'Kobe': 'Japan',
    
    'Seoul': 'South Korea',
    'Busan': 'South Korea',
    'Incheon': 'South Korea',
    
    'Mumbai': 'India',
    'Delhi': 'India',
    'Bangalore': 'India',
    'Chennai': 'India',
    'Kolkata': 'India',
    'Hyderabad': 'India',
    'Pune': 'India',
    'Ahmedabad': 'India',
    'Jaipur': 'India',
    'Surat': 'India',
    'Lucknow': 'India',
    'Kanpur': 'India',
    'Nagpur': 'India',
    'Visakhapatnam': 'India',
    'Bhopal': 'India',
    'Patna': 'India',
    'Kochi': 'India',
    'Thiruvananthapuram': 'India',
    'Chandigarh': 'India',
    'Gurugram': 'India',
    
    'Bangkok': 'Thailand',
    'Ho Chi Minh City': 'Vietnam',
    'Hanoi': 'Vietnam',
    'Manila': 'Philippines',
    'Jakarta': 'Indonesia',
    'Kuala Lumpur': 'Malaysia',
    
    'London': 'United Kingdom',
    'Manchester': 'United Kingdom',
    'Birmingham': 'United Kingdom',
    'Liverpool': 'United Kingdom',
    'Glasgow': 'United Kingdom',
    
    'Paris': 'France',
    'Lyon': 'France',
    'Marseille': 'France',
    'Toulouse': 'France',
    
    'Berlin': 'Germany',
    'Munich': 'Germany',
    'Hamburg': 'Germany',
    'Frankfurt': 'Germany',
    'Cologne': 'Germany',
    'Stuttgart': 'Germany',
    'Düsseldorf': 'Germany',
    
    'Milan': 'Italy',
    'Rome': 'Italy',
    'Naples': 'Italy',
    'Turin': 'Italy',
    'Genoa': 'Italy',
    
    'Madrid': 'Spain',
    'Barcelona': 'Spain',
    'Valencia': 'Spain',
    'Seville': 'Spain',
    
    'Amsterdam': 'Netherlands',
    'Rotterdam': 'Netherlands',
    'The Hague': 'Netherlands',
    
    'Zurich': 'Switzerland',
    'Geneva': 'Switzerland',
    'Basel': 'Switzerland',
    
    'Vienna': 'Austria',
    'Brussels': 'Belgium',
    'Antwerp': 'Belgium',
    'Stockholm': 'Sweden',
    'Copenhagen': 'Denmark',
    'Oslo': 'Norway',
    'Helsinki': 'Finland',
    'Warsaw': 'Poland',
    'Prague': 'Czech Republic',
    'Budapest': 'Hungary',
    
    'New York': 'United States',
    'Los Angeles': 'United States',
    'Chicago': 'United States',
    'Houston': 'United States',
    'Phoenix': 'United States',
    'Philadelphia': 'United States',
    'San Antonio': 'United States',
    'San Diego': 'United States',
    'Dallas': 'United States',
    'San Jose': 'United States',
    'Austin': 'United States',
    'Jacksonville': 'United States',
    'San Francisco': 'United States',
    'Seattle': 'United States',
    'Denver': 'United States',
    'Boston': 'United States',
    'Washington': 'United States',
    'Nashville': 'United States',
    'Baltimore': 'United States',
    'Louisville': 'United States',
    'Portland': 'United States',
    'Oklahoma City': 'United States',
    'Memphis': 'United States',
    'Las Vegas': 'United States',
    'Miami': 'United States',
    'Atlanta': 'United States',
    'Detroit': 'United States',
    'Cleveland': 'United States',
    'Pittsburgh': 'United States',
    'Minneapolis': 'United States',
    'Tampa': 'United States',
    'New Orleans': 'United States',
    'Cincinnati': 'United States',
    'Buffalo': 'United States',
    'Norfolk': 'United States',
    'Long Beach': 'United States',
    'Oakland': 'United States',
    'Savannah': 'United States',
    'Charleston': 'United States',
    
    'Toronto': 'Canada',
    'Vancouver': 'Canada',
    'Montreal': 'Canada',
    'Calgary': 'Canada',
    'Ottawa': 'Canada',
    'Edmonton': 'Canada',
    'Quebec City': 'Canada',
    'Winnipeg': 'Canada',
    'Hamilton': 'Canada',
    'Halifax': 'Canada',
    
    'Mexico City': 'Mexico',
    'Guadalajara': 'Mexico',
    'Monterrey': 'Mexico',
    'Tijuana': 'Mexico',
    'Puebla': 'Mexico',
    
    'São Paulo': 'Brazil',
    'Rio de Janeiro': 'Brazil',
    'Brasília': 'Brazil',
    'Salvador': 'Brazil',
    'Fortaleza': 'Brazil',
    'Belo Horizonte': 'Brazil',
    'Manaus': 'Brazil',
    'Curitiba': 'Brazil',
    'Recife': 'Brazil',
    'Porto Alegre': 'Brazil',
    'Santos': 'Brazil',
    
    'Buenos Aires': 'Argentina',
    'Santiago': 'Chile',
    'Lima': 'Peru',
    'Bogotá': 'Colombia',
    'Caracas': 'Venezuela',
    'Montevideo': 'Uruguay',
    'Quito': 'Ecuador',
    'La Paz': 'Bolivia',
    'Asunción': 'Paraguay',
    
    'Sydney': 'Australia',
    'Melbourne': 'Australia',
    'Brisbane': 'Australia',
    'Perth': 'Australia',
    'Adelaide': 'Australia',
    'Darwin': 'Australia',
    'Hobart': 'Australia',
    'Fremantle': 'Australia',
    
    'Auckland': 'New Zealand',
    'Wellington': 'New Zealand',
    'Christchurch': 'New Zealand',
    
    'Moscow': 'Russia',
    'St. Petersburg': 'Russia',
    'Novosibirsk': 'Russia',
    'Yekaterinburg': 'Russia',
    'Nizhny Novgorod': 'Russia',
    'Kazan': 'Russia',
    'Chelyabinsk': 'Russia',
    'Omsk': 'Russia',
    'Samara': 'Russia',
    'Rostov-on-Don': 'Russia',
    'Ufa': 'Russia',
    'Krasnoyarsk': 'Russia',
    'Perm': 'Russia',
    'Volgograd': 'Russia',
    'Voronezh': 'Russia',
    'Vladivostok': 'Russia',
    
    'Cairo': 'Egypt',
    'Alexandria': 'Egypt',
    'Lagos': 'Nigeria',
    'Abuja': 'Nigeria',
    'Johannesburg': 'South Africa',
    'Cape Town': 'South Africa',
    'Durban': 'South Africa',
    'Pretoria': 'South Africa',
    'Casablanca': 'Morocco',
    'Rabat': 'Morocco',
    'Algiers': 'Algeria',
    'Tunis': 'Tunisia',
    'Nairobi': 'Kenya',
    'Addis Ababa': 'Ethiopia',
    'Accra': 'Ghana',
    'Dakar': 'Senegal',
    
    'Istanbul': 'Turkey',
    'Ankara': 'Turkey',
    'Izmir': 'Turkey',
    'Bursa': 'Turkey',
    
    'Tel Aviv': 'Israel',
    'Jerusalem': 'Israel',
    'Haifa': 'Israel',
    
    'Dubai': 'United Arab Emirates',
    'Abu Dhabi': 'United Arab Emirates',
    'Sharjah': 'United Arab Emirates',
    
    'Riyadh': 'Saudi Arabia',
    'Jeddah': 'Saudi Arabia',
    'Mecca': 'Saudi Arabia',
    'Medina': 'Saudi Arabia',
    
    'Tehran': 'Iran',
    'Isfahan': 'Iran',
    'Mashhad': 'Iran',
    'Tabriz': 'Iran',
    
    'Baghdad': 'Iraq',
    'Basra': 'Iraq',
    'Mosul': 'Iraq',
    
    'Kuwait City': 'Kuwait',
    'Doha': 'Qatar',
    'Manama': 'Bahrain',
    'Muscat': 'Oman',
    
    'Karachi': 'Pakistan',
    'Lahore': 'Pakistan',
    'Islamabad': 'Pakistan',
    'Faisalabad': 'Pakistan',
    
    'Dhaka': 'Bangladesh',
    'Chittagong': 'Bangladesh',
    
    'Colombo': 'Sri Lanka',
    
    'Kathmandu': 'Nepal',
    'Kabul': 'Afghanistan',
}

# Terminology-to-Country mapping for location inference based on specific terms
# within this mapping, we also include US states
TERMINOLOGY_TO_COUNTRY = {
    # US State Names
    'California': 'United States',
    'Texas': 'United States',
    'Florida': 'United States',
    'New York': 'United States',
    'Illinois': 'United States',
    'Pennsylvania': 'United States',
    'Ohio': 'United States',
    'Georgia': 'United States',
    'North Carolina': 'United States',
    'Michigan': 'United States',
    'New Jersey': 'United States',
    'Virginia': 'United States',
    'Washington': 'United States',
    'Arizona': 'United States',
    'Massachusetts': 'United States',
    'Tennessee': 'United States',
    'Indiana': 'United States',
    'Missouri': 'United States',
    'Maryland': 'United States',
    'Wisconsin': 'United States',
    'Colorado': 'United States',
    'Minnesota': 'United States',
    'South Carolina': 'United States',
    'Alabama': 'United States',
    'Louisiana': 'United States',
    'Kentucky': 'United States',
    'Oregon': 'United States',
    'Oklahoma': 'United States',
    'Connecticut': 'United States',
    'Iowa': 'United States',
    'Mississippi': 'United States',
    'Arkansas': 'United States',
    'Kansas': 'United States',
    'Utah': 'United States',
    'Nevada': 'United States',
    'New Mexico': 'United States',
    'West Virginia': 'United States',
    'Nebraska': 'United States',
    'Idaho': 'United States',
    'Hawaii': 'United States',
    'Maine': 'United States',
    'New Hampshire': 'United States',
    'Rhode Island': 'United States',
    'Delaware': 'United States',
    'Montana': 'United States',
    'Wyoming': 'United States',
    'South Dakota': 'United States',
    'North Dakota': 'United States',
    'Alaska': 'United States',
    'Vermont': 'United States',
    'District of Columbia': 'United States',  # Washington D.C.

    # Currency and financial terms
    'lakh': 'India',                    # Indian numbering system
    'crore': 'India',                   # Indian numbering system  
    'rupees': 'India',                  # Indian currency
    'pounds': 'United Kingdom',         # British currency
    'sterling': 'United Kingdom',       # British currency
    'yen': 'Japan',                     # Japanese currency
    'yuan': 'China',                    # Chinese currency
    'renminbi': 'China',                # Chinese currency
    'ruble': 'Russia',                  # Russian currency
    'peso': 'Mexico',                   # Mexican currency (also used in other countries)
    'canadian dollar': 'Canada',        # Canadian currency
    'australian dollar': 'Australia',   # Australian currency
    
    # Government and institutional terms
    'bundestag': 'Germany',             # German parliament
    'duma': 'Russia',                   # Russian parliament
    'lok sabha': 'India',               # Indian parliament lower house
    'rajya sabha': 'India',             # Indian parliament upper house
    
    # Cultural and regional terms
    'bollywood': 'India',               # Indian film industry
    'hollywood': 'United States',       # American film industry
    'Thames': 'United Kingdom'          # River in the UK, often associated with London
}

def extract_countries_from_text(text: str) -> List[str]:
    """
    Extract country names from text using Named Entity Recognition.
    If no countries are found, attempt to infer countries from city names or terminology.
    
    Args:
        text (str): The text to analyze
        
    Returns:
        List[str]: List of standardized country names found in the text
    """
    if not nlp:
        return []
    
    # Convert text to lowercase for terminology matching
    text_lower = text.lower()
    
    # Process the text with spaCy
    # doc = nlp(text)  # NER model disabled
    
    # Extract entities labeled as GPE (Geopolitical entities) or LOC (Locations)
    countries = set()
    cities = set()
    terminology_countries = set()
    
    # Check for terminology-based country inference
    for term, country in TERMINOLOGY_TO_COUNTRY.items():
        if term.lower() in text_lower:
            if country in VALID_COUNTRIES:
                terminology_countries.add(country)
    
    # Extract named entities
    for ent in doc.ents:
        if ent.label_ in ['GPE', 'LOC']:
            # Clean and standardize the entity text
            entity_text = ent.text.strip()
            
            # Skip if it's a known non-country entity
            if entity_text in NON_COUNTRIES:
                continue
            
            # First check if it standardizes to a valid country
            if entity_text in COUNTRY_STANDARDIZATION:
                standardized_name = COUNTRY_STANDARDIZATION[entity_text]
                if standardized_name in VALID_COUNTRIES:
                    countries.add(standardized_name)
            # Then check if the original entity is a valid country
            elif entity_text in VALID_COUNTRIES:
                countries.add(entity_text)
            # If not a country, check if it's a known city
            elif entity_text in CITY_TO_COUNTRY:
                cities.add(entity_text)
            # Skip other entities (likely cities we don't have mappings for)
    
    # Priority order for country inference:
    # 1. Direct country mentions (highest priority)
    # 2. Terminology-based inference
    # 3. City-based inference (lowest priority)
    
    if countries:
        # If direct countries found, also include terminology countries
        final_countries = countries.union(terminology_countries)
    elif terminology_countries:
        # If no direct countries but terminology found, use terminology
        final_countries = terminology_countries
    elif cities:
        # If no countries or terminology, infer from cities
        final_countries = set()
        for city in cities:
            country = CITY_TO_COUNTRY[city]
            final_countries.add(country)
    else:
        final_countries = set()
    
    return sorted(list(final_countries))

def extract_countries_from_article(article: Dict) -> List[str]:
    """
    Extract countries from a news article.
    
    Args:
        article (dict): Article dictionary with title, description, content
        
    Returns:
        List[str]: List of countries mentioned in the article
    """
    # Combine all available text from the article
    title = article.get('title', '')
    description = article.get('description', '')
    content = article.get('content', '')
    
    # Combine all text
    full_text = f"{title} {description} {content}"
    
    # Extract countries
    countries = extract_countries_from_text(full_text)
    
    return countries

def process_articles_for_countries(articles: List[Dict]) -> Dict[str, List[str]]:
    """
    Process multiple articles to extract countries from each.
    
    Args:
        articles (List[Dict]): List of article dictionaries
        
    Returns:
        Dict[str, List[str]]: Dictionary mapping article URLs to country lists
    """
    results = {}
    
    for article in articles:
        url = article.get('url', '')
        countries = extract_countries_from_article(article)
        if countries:  # Only store if countries were found
            results[url] = countries
    
    return results

def get_country_statistics(articles: List[Dict]) -> Dict[str, int]:
    """
    Get statistics on how often each country appears across all articles.
    
    Args:
        articles (List[Dict]): List of article dictionaries
        
    Returns:
        Dict[str, int]: Dictionary of country names and their frequency counts
    """
    country_counts = {}
    
    for article in articles:
        countries = extract_countries_from_article(article)
        for country in countries:
            country_counts[country] = country_counts.get(country, 0) + 1
    
    # Sort by frequency (most mentioned first)
    return dict(sorted(country_counts.items(), key=lambda x: x[1], reverse=True))

def load_news_cache() -> List[Dict]:
    """Load articles from the news cache file."""
    cache_file = 'news_cache.json'
    if os.path.exists(cache_file):
        try:
            with open(cache_file, 'r') as f:
                cache_data = json.load(f)
                return cache_data.get('data', [])
        except (json.JSONDecodeError, ValueError):
            return []
    return []

# Cache file path for countries
COUNTRY_CACHE_FILE = 'country_cache.json'

def load_country_cache():
    """Load the country cache file."""
    if os.path.exists(COUNTRY_CACHE_FILE):
        try:
            with open(COUNTRY_CACHE_FILE, 'r') as f:
                cache_data = json.load(f)
                # Convert timestamp string back to datetime if needed
                if cache_data.get('timestamp'):
                    from datetime import datetime
                    cache_data['timestamp'] = datetime.fromisoformat(cache_data['timestamp'])
                return cache_data
        except (json.JSONDecodeError, ValueError):
            return {'data': {}, 'timestamp': None}
    return {'data': {}, 'timestamp': None}

def save_country_cache(country_data, timestamp=None):
    """Save country data to cache file."""
    if timestamp is None:
        from datetime import datetime
        timestamp = datetime.now()
    
    cache_data = {
        'data': country_data,
        'timestamp': timestamp.isoformat()  # Convert datetime to string for JSON
    }
    
    with open(COUNTRY_CACHE_FILE, 'w') as f:
        json.dump(cache_data, f, indent=2)

def process_and_cache_countries(articles):
    """
    Process articles for country extraction and save to cache.
    
    Args:
        articles (List[Dict]): List of article dictionaries
        
    Returns:
        Dict[str, List[str]]: Country data that was cached
    """
    print("Processing articles for country extraction...")
    
    # Extract countries from all articles
    country_data = process_articles_for_countries(articles)
    
    # Save to cache
    from datetime import datetime
    save_country_cache(country_data, datetime.now())
    
    print(f"Country extraction complete. Found countries in {len(country_data)} articles.")
    
    return country_data

def get_article_countries_from_cache(article_url):
    """
    Get countries for a specific article from cache.
    
    Args:
        article_url (str): The URL of the article
        
    Returns:
        List[str]: List of countries for the article, or empty list if not found
    """
    cache = load_country_cache()
    return cache.get('data', {}).get(article_url, [])

def get_unique_countries_from_cache():
    """Extract unique countries from country_cache.json"""
    try:
        with open('country_cache.json', 'r', encoding='utf-8') as f:
            cache_data = json.load(f)
        
        unique_countries = set()
        for url, countries in cache_data.get('data', {}).items():
            if countries:  # Only add if countries list is not empty
                unique_countries.update(countries)
        
        return sorted(list(unique_countries))
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def map_countries_to_iso_codes(countries):
    """Map country names to ISO 3-letter codes for choropleth map"""
    country_mapping = {
        'United States': 'USA',
        'United Kingdom': 'GBR',
        'Canada': 'CAN',
        'Australia': 'AUS',
        'India': 'IND',
        'China': 'CHN',
        'Japan': 'JPN',
        'Germany': 'DEU',
        'France': 'FRA',
        'Italy': 'ITA',
        'Spain': 'ESP',
        'Brazil': 'BRA',
        'Russia': 'RUS',
        'South Africa': 'ZAF',
        'Mexico': 'MEX',
        'Argentina': 'ARG',
        'Chile': 'CHL',
        'South Korea': 'KOR',
        'Thailand': 'THA',
        'Vietnam': 'VNM',
        'Indonesia': 'IDN',
        'Malaysia': 'MYS',
        'Singapore': 'SGP',
        'Philippines': 'PHL',
        'Turkey': 'TUR',
        'Egypt': 'EGY',
        'Nigeria': 'NGA',
        'Kenya': 'KEN',
        'Morocco': 'MAR',
        'Israel': 'ISR',
        'Iran': 'IRN',
        'Saudi Arabia': 'SAU',
        'UAE': 'ARE',
        'Qatar': 'QAT',
        'Kuwait': 'KWT',
        'Jordan': 'JOR',
        'Lebanon': 'LBN',
        'Syria': 'SYR',
        'Iraq': 'IRQ',
        'Pakistan': 'PAK',
        'Bangladesh': 'BGD',
        'Sri Lanka': 'LKA',
        'Nepal': 'NPL',
        'Afghanistan': 'AFG',
        'Kazakhstan': 'KAZ',
        'Uzbekistan': 'UZB',
        'Ukraine': 'UKR',
        'Poland': 'POL',
        'Czech Republic': 'CZE',
        'Hungary': 'HUN',
        'Romania': 'ROU',
        'Bulgaria': 'BGR',
        'Greece': 'GRC',
        'Norway': 'NOR',
        'Sweden': 'SWE',
        'Denmark': 'DNK',
        'Finland': 'FIN',
        'Netherlands': 'NLD',
        'Belgium': 'BEL',
        'Switzerland': 'CHE',
        'Austria': 'AUT',
        'Portugal': 'PRT',
        'Ireland': 'IRL',
        'New Zealand': 'NZL',
    }
    
    # Create lists for choropleth
    iso_codes = []
    country_names = []
    values = []
    
    for country in countries:
        if country in country_mapping:
            iso_codes.append(country_mapping[country])
            country_names.append(country)
            values.append(1)  # All countries get value 1 for now (just highlighting presence)
    
    return iso_codes, country_names, values

def test_country_extraction():
    """Test the country extraction functionality."""
    print("Testing Country Extraction with NER")
    print("=" * 50)
    
    # Test with sample text containing countries
    test_text1 = """
    TSMC, Taiwan's largest semiconductor manufacturer, reported strong earnings.
    The company exports chips to the United States, China, and European markets.
    Trade tensions between US and China could impact global supply chains.
    """
    
    print("Test 1 - Text with Countries:")
    print(test_text1)
    print("\nExtracted Countries:")
    countries1 = extract_countries_from_text(test_text1)
    for i, country in enumerate(countries1, 1):
        print(f"{i}. {country}")
    
    # Test with sample text containing only cities (fallback scenario)
    test_text2 = """
    Shanghai port reported delays due to congestion. Manufacturing in Shenzhen
    has been affected by power shortages. Companies in Tokyo and Seoul are
    monitoring the situation closely.
    """
    
    print("\nTest 2 - Text with Cities Only (Fallback):")
    print(test_text2)
    print("\nExtracted Countries (inferred from cities):")
    countries2 = extract_countries_from_text(test_text2)
    for i, country in enumerate(countries2, 1):
        print(f"{i}. {country}")
    
    # Test with sample text containing terminology indicators
    test_text3 = """
    The company reported losses of 5 lakh rupees due to supply chain disruptions.
    Meanwhile, British firms are spending millions of pounds on inventory.
    The Japanese yen has strengthened affecting export costs.
    """
    
    print("\nTest 3 - Text with Terminology Indicators:")
    print(test_text3)
    print("\nExtracted Countries (inferred from terminology):")
    countries3 = extract_countries_from_text(test_text3)
    for i, country in enumerate(countries3, 1):
        print(f"{i}. {country}")
    
    # Test with mixed content (countries + terminology)
    test_text4 = """
    India's manufacturing sector grew despite monsoon challenges.
    The government invested 2 crore rupees in infrastructure projects.
    """
    
    print("\nTest 4 - Mixed Content (Countries + Terminology):")
    print(test_text4)
    print("\nExtracted Countries (direct + terminology):")
    countries4 = extract_countries_from_text(test_text4)
    for i, country in enumerate(countries4, 1):
        print(f"{i}. {country}")
    
    # Test with real articles from cache
    print("\n" + "=" * 50)
    print("Testing with Cached Articles")
    print("=" * 50)
    
    articles = load_news_cache()
    if articles:
        print(f"Found {len(articles)} articles in cache")
        
        # Test first 3 articles
        for i, article in enumerate(articles[:3]):
            print(f"\nArticle {i+1}: {article.get('title', 'Unknown')[:60]}...")
            countries = extract_countries_from_article(article)
            if countries:
                print(f"Countries found: {', '.join(countries)}")
            else:
                print("No countries detected")
        
        # Show overall statistics
        print("\n" + "=" * 50)
        print("Country Statistics Across All Articles")
        print("=" * 50)
        
        stats = get_country_statistics(articles)
        for country, count in list(stats.items())[:10]:  # Top 10
            print(f"{country}: {count} articles")
            
    else:
        print("No articles found in cache. Please run the main app first to fetch news.")

if __name__ == "__main__":
    # Check if spaCy model is available
    if nlp is None:
        print("Cannot run tests - spaCy model not available")
        print("Please install with: python -m spacy download en_core_web_sm")
    else:
        test_country_extraction()
