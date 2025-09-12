# Streamlit Community Cloud Deployment Guide

## GitHub Repository Setup

### 1. Create GitHub Repository
```bash
# Initialize git repository (if not already done)
git init

# Create repository on GitHub.com:
# - Go to github.com/new
# - Name: "novakid-placement-test" 
# - Description: "AI-powered English placement test for Novakid students"
# - Set to Public (required for free Streamlit hosting)
# - Don't initialize with README (you already have files)

# Add remote origin (replace YOUR_USERNAME)
git remote add origin https://github.com/YOUR_USERNAME/novakid-placement-test.git

# Add and commit all files
git add .
git status  # verify files are staged correctly
git commit -m "Initial commit: Novakid placement test app with Streamlit deployment config"

# Push to GitHub
git push -u origin main
```

## Streamlit Community Cloud Deployment

### 2. Deploy to Streamlit Cloud

1. **Go to Streamlit Cloud**
   - Visit: https://share.streamlit.io/
   - Sign in with your GitHub account

2. **Create New App**
   - Click "New app"
   - Repository: `YOUR_USERNAME/novakid-placement-test`
   - Branch: `main`
   - Main file path: `app.py`
   - App URL: `novakid-placement-test` (or custom name)

3. **Configure Secrets**
   - In your app dashboard → Settings → Secrets
   - Add the following (replace with your actual API keys):

```toml
[gemini]
api_key = "your_actual_gemini_api_key"

[unsplash]
access_key = "your_actual_unsplash_access_key"

[novakid_tts]
base_url = "https://cdn.novakidschool.com/api/0/text_to_speech"
```

4. **Deploy**
   - Click "Deploy!"
   - Your app will be available at: `https://novakid-placement-test.streamlit.app/`

### 3. Verify Deployment

✅ **Check these work:**
- App loads without errors
- Questions display correctly
- Audio playback works
- Images load from Unsplash
- Test completion and results screen

## Files Included in Deployment

### ✅ Ready for Production:
- `app.py` - Main Streamlit application
- `requirements.txt` - Python dependencies
- `data/questions.json` - Question bank (197KB, included in repo)
- `data/curriculum/` - Level definitions and competencies
- `.streamlit/config.toml` - App configuration with kid-friendly theme
- All `lib/` modules for adaptive engine, question rendering, analysis

### 🔒 Excluded from Git:
- `.env` - Local environment variables
- `.streamlit/secrets.toml` - Local secrets (template only)
- `data/test_results/` - User test results

## API Key Requirements

You'll need these API keys configured in Streamlit Cloud secrets:

1. **Google Gemini API Key** (required)
   - For question generation and analysis
   - Get from: https://ai.google.dev/

2. **Unsplash Access Key** (recommended)
   - For vocabulary images
   - Get from: https://unsplash.com/developers

3. **Novakid TTS URL** (optional)
   - Already configured with fallback URL
   - Contact Novakid for production API access

## Cost: $0 💰

- Streamlit Community Cloud: Free
- Questions stored in repository: Free
- GitHub public repository: Free
- Only API calls may incur costs (pay-per-use)

## Automatic Updates

Once deployed, any `git push` to your main branch will automatically redeploy your app! 🚀