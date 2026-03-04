# 🚀 Deployment Guide

This guide covers deploying the SCM Disruption Dashboard securely with hidden API keys.

## 🔒 Security Overview

This project implements best practices for API key management:

- **Local Development**: API keys loaded from `.env` file (excluded from git)
- **Streamlit Cloud**: API keys managed via Streamlit secrets (never exposed)
- **GitHub**: Private information protected by `.gitignore`

## Local Development Setup

### 1. Configure Environment Variables

```bash
# Copy the example file
cp .env.example .env

# Edit .env with your API keys
nano .env
```

Add your keys:
```
NEWSAPI_KEY=your_newsapi_key_here
GEMINI_API_KEY=your_gemini_api_key_here
```

### 2. Install Dependencies

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3. Run Locally

```bash
streamlit run app.py
```

The app will automatically load API keys from your `.env` file.

---

## Streamlit Cloud Deployment (Free Tier)

### Step 1: Prepare Your GitHub Repository

1. **Make sure `.env` is not tracked**
   ```bash
   git status  # Should NOT show .env
   ```

2. **Commit your code (without secrets)**
   ```bash
   git add .
   git commit -m "Update deployment configuration"
   git push origin main
   ```

### Step 2: Create Streamlit Cloud Account

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Sign in with your GitHub account
3. Click "New app"

### Step 3: Deploy Your App

1. Select your repository and branch
2. In "Advanced settings", configure your secrets:

   **Method 1: Paste TOML Format**
   ```toml
   [secrets]
   NEWSAPI_KEY = "your_actual_newsapi_key"
   GEMINI_API_KEY = "your_actual_gemini_api_key"
   ```

   **Method 2: Environment Variables**
   Set as environment secrets in Streamlit's dashboard

3. Click "Deploy"

### Step 4: Verify Deployment

- Your app will be live within minutes
- Streamlit will display the URL (e.g., `https://your-app.streamlit.app`)
- API keys are stored securely and not visible in the code

---

## Troubleshooting

### "API Key not found" Error

**Local Development:**
- Check if `.env` file exists
- Verify keys are spelled correctly: `NEWSAPI_KEY`, `GEMINI_API_KEY`
- Ensure `.env` is in the project root directory
- Reload the app: `streamlit run app.py`

**Streamlit Cloud:**
- Go to app settings
- Click "Secrets" in the bottom menu
- Verify secrets are set correctly
- Redeploy the app from settings

### Keys Still Visible in Deployment

Check your code wasn't pushed with hardcoded keys:
```bash
git log --all --full-history -- api_keys.py
git log --all --full-history -- app.py | head -20
```

If keys were committed:
1. Rotate your API keys immediately
2. Use git filter-branch to remove sensitive commits (advanced)
3. Recommit without keys

---

## How It Works

### Loading Priority

The `api_keys.py` module attempts to load secrets in this order:

```
1. Streamlit Secrets (Running in Streamlit Cloud)
   ↓ (if not found)
2. Environment Variables (from .env or system environment)
   ↓ (if still not found)
3. Error: API Keys not configured
```

This allows:
- **Local development** with `.env`
- **Cloud deployment** with Streamlit secrets
- **CI/CD pipelines** with environment variables

---

## Files Overview

### Security-Related Files

- **.gitignore**: Excludes secrets and sensitive files
- **.env.example**: Template showing required environment variables
- **.streamlit/secrets.toml.example**: Template for Streamlit secrets
- **.streamlit/config.toml**: Streamlit configuration (safe to commit)

### Modified Files

- **api_keys.py**: Now dynamically loads keys from Streamlit/environment
- **app.py**: Loads `.env` file for local development
- **requirements.txt**: Added `python-dotenv` dependency

---

## Best Practices

✅ **Do:**
- Rotate API keys regularly
- Use `.env.example` for documentation
- Deploy via Streamlit Cloud for simplicity
- Review `.gitignore` before committing

❌ **Don't:**
- Commit `.env` or `api_keys.py` with real keys
- Share API keys in issues or pull requests
- Use API keys directly in code
- Deploy with keys in environment variables visible in logs

---

## Getting API Keys

### NewsAPI Key
1. Visit [newsapi.org](https://newsapi.org)
2. Sign up for free account
3. Copy your API key from the dashboard

### Google Generative AI (Gemini) Key
1. Visit [ai.google.dev](https://ai.google.dev)
2. Create a new project
3. Enable the Generative Language API
4. Create an API key from the credentials page

---

## Need Help?

- Review Streamlit's [secrets management docs](https://docs.streamlit.io/deploy/streamlit-cloud/deploy-your-app/secrets-management)
- Check [python-dotenv documentation](https://python-dotenv.readthedocs.io/)
- Review `.gitignore` structure for what's excluded
