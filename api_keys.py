# API Keys Configuration
# This module loads API keys from Streamlit secrets or environment variables
# DO NOT hardcode API keys here

import os
import sys

def load_api_keys():
    """
    Load API keys from Streamlit secrets (production) or environment variables (development).
    Priority:
    1. Streamlit secrets (for Streamlit Cloud deployments)
    2. Environment variables (for local development)
    3. Raise error if keys are not found
    """
    try:
        import streamlit as st
        # Try to load from Streamlit secrets
        try:
            newsapi_key = st.secrets.get("NEWSAPI_KEY")
            gemini_key = st.secrets.get("GEMINI_API_KEY")
        except Exception:
            # Fallback to environment variables if secrets not available
            newsapi_key = os.getenv("NEWSAPI_KEY")
            gemini_key = os.getenv("GEMINI_API_KEY")
    except ImportError:
        # If not in a Streamlit context, use environment variables
        newsapi_key = os.getenv("NEWSAPI_KEY")
        gemini_key = os.getenv("GEMINI_API_KEY")
    
    # Validate keys are present
    if not newsapi_key:
        raise ValueError(
            "NEWSAPI_KEY not found. Please set it in:\n"
            "  - Production: Streamlit Cloud secrets\n"
            "  - Local: .env file or environment variable"
        )
    
    if not gemini_key:
        raise ValueError(
            "GEMINI_API_KEY not found. Please set it in:\n"
            "  - Production: Streamlit Cloud secrets\n"
            "  - Local: .env file or environment variable"
        )
    
    return newsapi_key, gemini_key

# Load keys when module is imported
try:
    NEWSAPI_KEY, GEMINI_API_KEY = load_api_keys()
except ValueError as e:
    print(f"Error loading API keys: {e}", file=sys.stderr)
    # Set to None for debugging purposes
    NEWSAPI_KEY = None
    GEMINI_API_KEY = None
