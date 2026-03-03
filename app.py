import streamlit as st
from data_fetcher import fetch_news, get_articles_by_category, get_category_overview
from data_filtering import filter_by_keyword, filter_by_source, sort_by_date
from impact_assessment import assess_and_format_title
from country_extraction import get_article_countries_from_cache, get_unique_countries_from_cache, map_countries_to_iso_codes
from LLM_Article_Analysis import get_article_analysis
from datetime import datetime
import os
import plotly.graph_objects as go
import json

# Custom CSS for the settings popup and tooltips
st.markdown("""
<style>
.dashboard-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 2rem;
}
.settings-button {
    background: none;
    border: none;
    font-size: 1.5rem;
    cursor: pointer;
    padding: 0.5rem;
    border-radius: 50%;
    transition: background-color 0.2s;
}
.settings-button:hover {
    background-color: #f0f2f6;
}
.tooltip-container {
    position: relative;
    display: inline-block;
    cursor: pointer;
}
.tooltip {
    visibility: hidden;
    min-width: 300px;
    max-width: 500px;
    background-color: #333;
    color: #fff;
    text-align: left;
    border-radius: 6px;
    padding: 12px 16px;
    position: absolute;
    z-index: 1000;
    bottom: 125%;
    left: 50%;
    transform: translateX(-50%);
    opacity: 0;
    transition: opacity 0.3s;
    font-size: 13px;
    line-height: 1.4;
    box-shadow: 0px 4px 12px rgba(0,0,0,0.3);
    white-space: normal;
    word-wrap: break-word;
}
.tooltip::after {
    content: "";
    position: absolute;
    top: 100%;
    left: 50%;
    margin-left: -5px;
    border-width: 5px;
    border-style: solid;
    border-color: #333 transparent transparent transparent;
}
.tooltip-container:hover .tooltip {
    visibility: visible;
    opacity: 1;
}
.loading-container {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 2rem;
    min-height: 200px;
}
.loading-spinner {
    border: 4px solid #f3f3f3;
    border-top: 4px solid #1f77b4;
    border-radius: 50%;
    width: 50px;
    height: 50px;
    animation: spin 1s linear infinite;
    margin-bottom: 1rem;
}
@keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}
.loading-text {
    font-size: 1.1rem;
    color: #555;
    text-align: center;
    margin-bottom: 0.5rem;
}
.loading-subtitle {
    font-size: 0.9rem;
    color: #777;
    text-align: center;
}
</style>
""", unsafe_allow_html=True)

# Dashboard header with settings
header_col1, header_col2 = st.columns([4, 1])

with header_col1:
    st.title("Global Supply Chain Disruption Dashboard")

with header_col2:
    # Settings popup menu
    with st.popover("⚙️", help="Dashboard Settings"):
        
        # Show last update time
        def get_cache_timestamp():
            cache_file = 'news_cache.json'
            if os.path.exists(cache_file):
                timestamp = os.path.getmtime(cache_file)
                return datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")
            return "Unknown"
        
        st.write(f"**Last Updated:** {get_cache_timestamp()}")

# Loading screen and data fetching
@st.cache_data(ttl=1800)  # Cache for 30 minutes to match file cache duration
def load_dashboard_data():
    """Load all dashboard data with progress tracking"""
    return fetch_news()

# Create loading screen
loading_placeholder = st.empty()
progress_placeholder = st.empty()
status_placeholder = st.empty()

with loading_placeholder.container():
    st.markdown("""
    <div class="loading-container">
        <div class="loading-spinner"></div>
        <div class="loading-text">🔄 Loading Supply Chain Dashboard...</div>
        <div class="loading-subtitle">Analyzing global supply chain disruptions</div>
    </div>
    """, unsafe_allow_html=True)

# Progress tracking
with progress_placeholder.container():
    progress_bar = st.progress(0)

with status_placeholder.container():
    status_text = st.empty()

try:
    # Step 1: Check cache
    status_text.text("� Checking cached data...")
    progress_bar.progress(20)
    
    # Step 2: Fetch/load news
    status_text.text("� Loading news articles...")
    progress_bar.progress(50)
    articles = load_dashboard_data()
    
    # Step 3: Prepare categories
    status_text.text("📂 Organizing categories...")
    progress_bar.progress(80)
    
    # Step 4: Complete
    status_text.text("✅ Dashboard ready!")
    progress_bar.progress(100)
    
    # Brief pause to show completion
    import time
    time.sleep(0.3)
    
except Exception as e:
    status_text.error(f"❌ Error loading data: {str(e)}")
    st.error("Failed to load dashboard data. Please refresh the page.")
    st.stop()

finally:
    # Clear all loading elements
    loading_placeholder.empty()
    progress_placeholder.empty()
    status_placeholder.empty()

# Define category tabs
all_categories = [
    'All',
    'Natural Disasters',
    'Geopolitical', 
    'Transportation',
    'Economic Crisis',
    'Health & Safety',
    'Regulatory',
    'Technology & Cyber',
    'Resource Shortage',
    'Corporate',
    'General'
]

# Filter categories to only show those with articles
categories_with_articles = ['All']  # Always include "All"

for category in all_categories[1:]:  # Skip "All" since we already added it
    if category == "General":
        # Check for "General Supply Chain" articles
        category_articles = get_articles_by_category(articles, "General Supply Chain")
    else:
        category_articles = get_articles_by_category(articles, category)
    
    if len(category_articles) > 0:
        categories_with_articles.append(category)

# Use the filtered categories for the radio buttons
categories = categories_with_articles

# Main view selector
view_type = st.sidebar.selectbox(
    "Select View Type:",
    ["📰 News Category View", "🌍 Geo-Location View"],
    index=0,
    help="Choose between news sorted by category or a map view"
)

if view_type == "📰 News Category View":
    st.sidebar.subheader("📂 Categories")
    selected_category = st.sidebar.selectbox(
        "Select a category:",
        categories,
        index=0,
        help="Choose a supply chain disruption category to view related news"
    )
    selected_view = "category"
    
elif view_type == "🌍 Geo-Location View":
    st.sidebar.subheader("🗺️ Geographic Options")
    geo_option = st.sidebar.selectbox(
        "Select geographic view:",
        ["🌍 World Map View"],
        index=0,
        help="Choose a geographic visualization"
    )
    selected_view = "geo"
    selected_category = None

# Handle different view types
if selected_view == "geo":
    # Geo-Location View
    st.header("🌍 Geo-Location View")
    st.caption("Geographic analysis of global supply chain disruptions")
    
    if geo_option == "🌍 World Map View":
                
        # Get unique countries from cache
        unique_countries = get_unique_countries_from_cache()
        
        if unique_countries:
            # Map countries to ISO codes for choropleth
            iso_codes, country_names, values = map_countries_to_iso_codes(unique_countries)
            
            # Create choropleth map with highlighted countries
            fig = go.Figure(data=go.Choropleth(
                locations=iso_codes,
                z=values,
                text=country_names,
                colorscale=[[0, '#ffcccc'], [1, '#cc0000']],  # Light red to dark red
                showscale=False,  # Hide color scale since all values are the same
                marker_line_color='darkgray',
                marker_line_width=0.5,
                hovertemplate='<b>%{text}</b><br>Supply Chain Disruption Detected<extra></extra>'
            ))
            
            # Show summary info
            st.info(f"🌍 **{len(unique_countries)} countries** with potential supply chain disruptions detected")
            
            
        else:
            # Fallback to empty map if no countries found
            fig = go.Figure(data=go.Choropleth(
                locations=[],
                z=[],
                colorscale='Reds',
                showscale=True,
                marker_line_color='darkgray',
                marker_line_width=0.5,
            ))
            st.info("No countries with supply chain disruptions found in current data.")
        
        fig.update_layout(
            title_text='<i>Select a Country to View Potential Supply Chain Disruptions</i>',
            geo=dict(
            showframe=False,
            showcoastlines=True,
            projection_type='equirectangular'
            ),
            height=600
        )
        
        # Display the interactive map with click events
        selected_data = st.plotly_chart(fig, use_container_width=True, on_select="rerun")
        
        # Handle country selection from map clicks
        selected_country = None
        if selected_data and 'selection' in selected_data and selected_data['selection']['points']:
            # Get the first selected point
            point = selected_data['selection']['points'][0]
            if 'text' in point:
                selected_country = point['text']
        
        st.divider()
        
        # Filter articles based on selected country
        if selected_country:
            st.subheader(f"📰 News Articles from {selected_country}")
            st.caption(f"Showing articles that mention {selected_country}")
            
            # Filter articles to only show those that mention the selected country
            filtered_articles = []
            for article in articles:
                article_url = article.get('url', '')
                article_countries = get_article_countries_from_cache(article_url)
                if article_countries and selected_country in article_countries:
                    filtered_articles.append(article)
            
            if filtered_articles:
                st.info(f"Found {len(filtered_articles)} articles mentioning {selected_country}")
            else:
                st.warning(f"No articles found mentioning {selected_country}")
        else:
            st.subheader("📰 All Supply Chain News")
            st.caption("Click on a country in the map above to filter articles by location")
            filtered_articles = articles
        
        # Sort articles by date
        filtered_articles = sort_by_date(filtered_articles)
        
        # Display articles
        if filtered_articles:
            for article in filtered_articles:
                with st.container():
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        # Assess impact and format title with badge
                        impact_title = assess_and_format_title(article)
                        
                        # Get countries for this article from cache
                        article_url = article.get('url', '')
                        countries = get_article_countries_from_cache(article_url)
                        
                        # Get LLM analysis for this article from cache
                        llm_analysis = get_article_analysis(article)
                        
                        # Format countries for tooltip
                        tooltip_parts = []
                        
                        if countries:
                            # Show up to 3 countries, with "and X more" if there are more
                            if len(countries) <= 3:
                                countries_text = f"🌍 Countries: {', '.join(countries)}"
                            else:
                                visible_countries = countries[:3]
                                remaining = len(countries) - 3
                                countries_text = f"🌍 Countries: {', '.join(visible_countries)} and {remaining} more"
                            tooltip_parts.append(countries_text)
                        
                        if llm_analysis and llm_analysis != "Supply chain impact analysis unavailable.":
                            analysis_text = f"🚢 Potential Supply Chain Impact:<br>{llm_analysis}"
                            tooltip_parts.append(analysis_text)
                        
                        # Combine parts or show fallback
                        if tooltip_parts:
                            tooltip_text = " <br> ".join(tooltip_parts)
                        else:
                            tooltip_text = "No additional information available"
                        
                        # Create tooltip wrapper for the title
                        tooltip_html = f"""
                        <div class="tooltip-container">
                            <h3 style="margin: 0; padding: 0;">{impact_title}</h3>
                            <span class="tooltip">{tooltip_text}</span>
                        </div>
                        """
                        st.markdown(tooltip_html, unsafe_allow_html=True)
                        
                        st.write(f"**Source:** {article.get('source', {}).get('name', 'Unknown')}")
                        st.write(f"**Published:** {article.get('publishedAt', 'Unknown')}")
                        
                        # Show categories for this article
                        article_categories = article.get('categories', [])
                        if article_categories:
                            primary_category = article_categories[0] if article_categories else "Uncategorized"
                            if len(article_categories) > 1:
                                st.caption(f"📁 Categories: {', '.join(article_categories)}")
                            else:
                                st.caption(f"📁 Category: {primary_category}")
                        
                        # Highlight countries mentioned in this article
                        if countries:
                            if selected_country and selected_country in countries:
                                # Highlight the selected country
                                other_countries = [c for c in countries if c != selected_country]
                                if other_countries:
                                    st.caption(f"🎯 **{selected_country}** | Also mentions: {', '.join(other_countries)}")
                                else:
                                    st.caption(f"🎯 **{selected_country}**")
                            else:
                                st.caption(f"🌍 Mentions: {', '.join(countries)}")
                        
                        st.write(article.get('description', 'No description'))
                        
                        if article.get('url'):
                            st.write(f"[Read more]({article['url']})")
                    
                    with col2:
                        # Show article image if available
                        if article.get('urlToImage'):
                            try:
                                st.image(article['urlToImage'], width=200)
                            except:
                                pass  # Skip if image fails to load
                
                st.divider()
        else:
            st.info("No articles available to display.")

elif selected_view == "category":
    # News Category View (existing functionality)
    # Display selected category content
    # Get articles for the selected category
    if selected_category == "All":
        category_articles = articles
        # Create a custom overview for "All" category
        overview = {
            'total_articles': len(articles),
            'sources': sorted(list(set([article.get('source', {}).get('name', '') 
                                      for article in articles 
                                      if article.get('source', {}).get('name')]))),
            'source_count': len(set([article.get('source', {}).get('name', '') 
                                   for article in articles 
                                   if article.get('source', {}).get('name')]))
        }
    elif selected_category == "General":
        # Map "General" to "General Supply Chain" for the backend
        category_articles = get_articles_by_category(articles, "General Supply Chain")
        overview = get_category_overview(articles, "General Supply Chain")
    else:
        category_articles = get_articles_by_category(articles, selected_category)
        overview = get_category_overview(articles, selected_category)

    # Display category header and overview
    st.header(f"{selected_category} News")

    # Add category descriptions
    category_descriptions = {
        'All': 'Comprehensive view of all potential supply chain disruption news across all categories.',
        'General': 'General news that may affect supply chain, logistics, or shipping.',
        'Natural Disasters': 'News on earthquakes, floods, and other natural disasters.',
        'Geopolitical': 'Trade wars, sanctions, and border closures.',
        'Transportation': 'Disruptions to ports, airports, and rail networks.',
        'Economic Crisis': 'Currency fluctuations, inflation, banking issues, and market crashes.',
        'Health & Safety': 'Pandemic-related impacts on supply chain.',
        'Regulatory': 'Export/import restrictions, trade policies, and customs regulations.',
        'Technology & Cyber': 'Cyberattacks, data breaches, and ransomware news.',
        'Resource Shortage': 'Shortages of chips, materials, energy, and labor resources.',
        'Corporate': 'Company-specific disruptions from major manufacturers and suppliers.'
    }

    if selected_category in category_descriptions:
        st.caption(category_descriptions[selected_category])

    # Source filtering section
    if overview['sources']:
        with st.expander("📰 Filter by Sources", expanded=False):
            st.write("Deselect sources you want to hide:")
            selected_sources = st.multiselect(
                "Choose sources to display:",
                options=overview['sources'],
                default=overview['sources'],  # All sources selected by default
                help="Deselect sources you want to filter out",
                label_visibility="collapsed"
            )
            
            if not selected_sources:
                st.warning("⚠️ Please select at least one source to display articles.")
    else:
        selected_sources = []

    st.divider()

    # Sort articles by date and filter by selected sources
    filtered_articles = sort_by_date(category_articles)

    # Apply source filtering if sources are selected
    if selected_sources and overview['sources']:
        filtered_articles = [
            article for article in filtered_articles
            if article.get('source', {}).get('name', '') in selected_sources
        ]

    if not filtered_articles:
        if not selected_sources:
            st.info("Please select at least one source to view articles.")
        else:
            st.info(f"No articles found in {selected_category} category with the selected sources.")
    else:
        # Show filtering info if sources are filtered
        if overview['sources'] and len(selected_sources) < len(overview['sources']):
            excluded_count = overview['total_articles'] - len(filtered_articles)
            st.info(f"Showing {len(filtered_articles)} articles (filtered out {excluded_count} from unselected sources)")
        
        # Display articles
        for article in filtered_articles:
            with st.container():
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    # Assess impact and format title with badge
                    impact_title = assess_and_format_title(article)
                    
                    # Get countries for this article from cache
                    article_url = article.get('url', '')
                    countries = get_article_countries_from_cache(article_url)
                    
                    # Get LLM analysis for this article from cache
                    llm_analysis = get_article_analysis(article)
                    
                    # Format countries for tooltip
                    tooltip_parts = []
                    
                    if countries:
                        # Show up to 3 countries, with "and X more" if there are more
                        if len(countries) <= 3:
                            countries_text = f"🌍 Countries: {', '.join(countries)}"
                        else:
                            visible_countries = countries[:3]
                            remaining = len(countries) - 3
                            countries_text = f"🌍 Countries: {', '.join(visible_countries)} and {remaining} more"
                        tooltip_parts.append(countries_text)
                    
                    if llm_analysis and llm_analysis != "Supply chain impact analysis unavailable.":
                        analysis_text = f"🚢 Potential Supply Chain Impact:<br>{llm_analysis}"
                        tooltip_parts.append(analysis_text)
                    
                    # Combine parts or show fallback
                    if tooltip_parts:
                        tooltip_text = " <br> ".join(tooltip_parts)
                    else:
                        tooltip_text = "No additional information available"
                    
                    # Create tooltip wrapper for the title
                    tooltip_html = f"""
                    <div class="tooltip-container">
                        <h3 style="margin: 0; padding: 0;">{impact_title}</h3>
                        <span class="tooltip">{tooltip_text}</span>
                    </div>
                    """
                    st.markdown(tooltip_html, unsafe_allow_html=True)
                    
                    st.write(f"**Source:** {article.get('source', {}).get('name', 'Unknown')}")
                    st.write(f"**Published:** {article.get('publishedAt', 'Unknown')}")
                    
                    # Show categories for this article
                    article_categories = article.get('categories', [])
                    if selected_category != "All" and len(article_categories) > 1:
                        # For specific categories, show other categories this article belongs to
                        display_category = "General Supply Chain" if selected_category == "General" else selected_category
                        other_categories = [cat for cat in article_categories if cat != display_category]
                        if other_categories:
                            st.caption(f"📁 Also in: {', '.join(other_categories)}")
                    elif selected_category == "All" and article_categories:
                        # For "All" view, show the primary category
                        primary_category = article_categories[0] if article_categories else "Uncategorized"
                        st.caption(f"📁 Category: {primary_category}")
                    
                    st.write(article.get('description', 'No description'))
                    
                    if article.get('url'):
                        st.write(f"[Read more]({article['url']})")
                
                with col2:
                    # Show article image if available
                    if article.get('urlToImage'):
                        try:
                            st.image(article['urlToImage'], width=200)
                        except:
                            pass  # Skip if image fails to load
            
            st.divider()
